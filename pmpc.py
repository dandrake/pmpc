#!/usr/bin/env python
"""display speaker notes

+/- keys to adjust text size

make text white on dark gray background

forward/back keys: j/k, left/right, up/down, pageup/pagedn, space, maybe
home/end for first/last

type a number, then "g" to change the notes to that slide without
changing mupdf; this lets you re-sync your notes and slides if they get
messed up

drive evince with subprocess running xdotool

http://zetcode.com/gui/tkinter/widgets/

nope, let's do mupdf; evince seems to not listen to keypresses when the window isn't focused (as will always be the case here), but mupdf does.

cairo & Tkinter: http://stackoverflow.com/a/26189022

http://www.ferg.org/thinking_in_tkinter/tt100_py.txt
"""
import sys
import os.path
import xml.etree.ElementTree as ET
import collections
import Tkinter
import PIL.Image, PIL.ImageTk
import cairo
import subprocess
import poppler
import time

# stolen from http://ethanschoonover.com/solarized
BG = '#002b36'
FG = '#eee8d5'

def join_with_blank_line(s, t):
    """
    for concatenating multiple <note> elements: this joins two strings
    with a blank line (\n\n); if either is empty, just returns s+t.
    """
    if s == '' or t == '':
        return s + t
    else:
        return s.rstrip('\n') + '\n\n' + t.lstrip('\n')

def parse_notes(fn):
    ret = collections.defaultdict(lambda: '')
    try:
        notes = ET.parse(fn).getroot()
    except IOError:
        ret[0] = '\nno file {}!'.format(fn)
        return ret
    except ET.ParseError as exc:
        print 'Parse error:'
        print exc
        print "Do you have a bare & or < somewhere? Change it to '&amp;' or '&lt;'."
        sys.exit(1)

    # normalize the notes: each starts with one \n, join multiple
    # <note>s for the same slide. Might experiment with: remove common
    # leading whitespace, remove single \n's (let the presenter do the
    # line breaks). (But are those two incompatible?)
    for note in notes:
        i = int(note.attrib['slide'])
        ret[i] = '\n' + join_with_blank_line(ret[i], note.text).lstrip('\n')
    return ret

def parse_indices_labels(labels):
    """
    For slides with overlays, we have multiple pages in the pdf but only
    one note. So we need a mapping from indices to the indices that you
    actually get in the notes. For example:

    page index, label:   
    0 1
    1 2
    2 3
    3 3
    4 4
    5 5
    6 5
    7 5

    The notes file has notes for slides 0, 1, 3, 4, 7. The pattern is
    reasonably clear: say page index k has label L(k). We want a mapping
    from k to the maximum index in the set L^(-1)(L(k)). (I'm a
    mathematician, thinking in terms of functions, sets, and inverses is
    natural.)

    The code below does that. Just give it a list of labels so that L(k)
    = labels[k] and it returns a dictionary. For the above situation,
    the dictionary is

    {0: 0, 1: 1, 2: 3, 3: 3, 4: 4, 5: 7, 6: 7, 7: 7}.
    """
    label_to_index = {}
    for n, label in enumerate(labels):
        label_to_index[label] = n
    # Now we have a mapping from page labels to the last page index with
    # that page label. Compose that with the index->label mapping:
    index_to_note_num = {}
    for n, label in enumerate(labels):
        index_to_note_num[n] = label_to_index[label]
    return index_to_note_num

class PoorMansPresenterConsole(Tkinter.Frame):
    def __init__(self, fn, parent):
        fn = os.path.splitext(fn)[0]
        self.notes = parse_notes(fn + '.notes.xml')
        self.pdf = fn + '.pdf'

        self.slide = 0
        self.document = poppler.document_new_from_file('file://' + os.path.abspath(self.pdf), None)
        self.nslides = self.document.get_n_pages()
        self.index_to_note_num = parse_indices_labels([
            self.document.get_page(n).get_label() for n in range(self.nslides)])

        Tkinter.Frame.__init__(self, parent, background=BG)

        self.nextkeys = ['j', 'J', 'Right', 'Down', 'Next', 'space']
        self.prevkeys = ['k', 'K', 'Left', 'Up', 'Prior', 'BackSpace']
        # store digits so you can re-sync slides & pdf
        self.digits = ''

        self.textsize = 20

        self.note = Tkinter.StringVar()

        self.thumbnail = self.get_thumbnail_page()

    def ui_init(self):
        """
        Do those UI initialization tasks that can't be done unless we
        know whether we're presenting or rehearsing.
        """
        self.slide_size = tuple(int(_) for _ in self.thumbnail.get_size())
        self.set_note()
        self.do_msg()

        # dummy just to get initial UI arrangement
        self.label = Tkinter.Label(self)
        self.label.pack(anchor='ne') #side=Tkinter.RIGHT, anchor='n')

        self.timer = Tkinter.Label(self, text="hit `t' to start timer",
                                   font=('Helvetica', 32, 'bold'),
                                   background=BG,
                                   fg=FG)
        self.timer.pack(anchor='center')
        self.start_time = 0

        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.slide_size[0], self.slide_size[1])
        self.context = cairo.Context(self.surface)
        self.shownote()

        self.focus_get()
        self.bind_all("<Key>", self.onKeyPressed)

    def get_thumbnail_page(self):
        """
        This returns a Poppler page object for the slide that will get
        thumbnailed. The idea is that we subclass this and
        either redefine this function to return the next slide (for
        presenting) or the current slide (for rehearsing).
        """
        pass

    def set_note(self):
        """
        Similar to above: this just sets the text of the note, but the
        Rehearser overrides this to add a reminder that you're
        rehearsing.
        """
        self.note.set('{}/{}: '.format(self.slide + 1, self.nslides) +
                      self.notes[self.index_to_note_num[self.slide]])

    def do_msg(self):
        """
        set up and pack the Message; only necessary when text size changes
        """
        try:
            self.msg.pack_forget()
        except AttributeError:
            # first time, just keep going
            pass
        width = max(500, self.winfo_width() - self.slide_size[0] - 10)
        self.msg = Tkinter.Message(self, textvariable=self.note,
                                   font=('Helvetica', self.textsize, 'bold'),
                                   background=BG,
                                   fg=FG,
                                   width=width,
                                   anchor='nw')
        self.msg.pack(side=Tkinter.LEFT, fill=Tkinter.BOTH, anchor='nw', expand=1)

    def shownote(self):
        # TODO: on window resize, adjust width of the Message; right now
        # only done on text resize
        # print 'width:', self.winfo_width()
        self.set_note()

        self.label.pack_forget()
        self.timer.pack_forget()

        self.thumbnail = self.get_thumbnail_page()
        if self.thumbnail is not None:
            self.thumbnail.render(self.context)
            self._image_ref = PIL.ImageTk.PhotoImage(PIL.Image.frombuffer("RGBA", self.slide_size, self.surface.get_data(), "raw", "BGRA", 0, 1))

            self.label = Tkinter.Label(self, image=self._image_ref)
            self.label.pack(anchor='ne') #side=Tkinter.RIGHT, anchor='n')

        self.timer.pack(anchor='center')

        self.pack(fill=Tkinter.BOTH, expand=1)

    def tick(self):
        t = int(time.time() - self.start_time)
        self.timer.configure(text='{}:{:02}'.format(t / 60, t % 60))
        self.timer.after(1000, self.tick)

    def onKeyPressed(self, e): 
        key = e.keysym
        print key
        if key == 'plus':
            self.textsize += 3
            self.do_msg()
            self.shownote()
        if key == 'minus':
            self.textsize -= 3
            self.do_msg()
            self.shownote()
        if key in self.nextkeys and self.slide < self.nslides - 1:
            self.slide += 1
            # no spaces in args, so okay to just .split()
            subprocess.call('/usr/bin/xdotool search mupdf key Next'.split())
            self.shownote()
        if key in self.prevkeys and self.slide > 0:
            self.slide -= 1
            subprocess.call('/usr/bin/xdotool search mupdf key Prior'.split())
            self.shownote()
        # store digits so we can re-sync to a certain slide
        if key in [str(n) for n in range(10)]:
            self.digits += key
            print 'digits now', self.digits
        if key == 'g':
            try:
                n = int(self.digits.lstrip('0')) - 1
            except ValueError:
                return
            if 0 <= n < self.nslides:
                self.slide = n
                self.shownote()
            self.digits = ''
        # state 4 is ctrl held down: http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/event-handlers.html
        if key == 'w' and e.state == 4:
            sys.exit(0)
        if key == 't':
            if self.start_time == 0:
                self.start_time = time.time()
            self.tick()
        if key == 'Home':
            self.slide = 0
            subprocess.call('/usr/bin/xdotool search mupdf key g'.split())
            self.shownote()
        if key == 'End':
            self.slide = self.nslides - 1
            subprocess.call('/usr/bin/xdotool search mupdf key G'.split())
            self.shownote()

        if key == 'a':
            subprocess.call('/usr/bin/xdotool search iclicker windowfocus key ctrl+g'.split())
            subprocess.call('/usr/bin/xdotool search Presenting windowactivate'.split())

class Presenter(PoorMansPresenterConsole):
    def __init__(self, fn, parent):
        PoorMansPresenterConsole.__init__(self, fn, parent)
        parent.title('Presenting {}'.format(self.pdf))

        self.notes[0] = "\nDo `f', then `W' to fullscreen mupdf.\n" + self.notes[0]

        self.ui_init()
        self.mupdf_pid = subprocess.Popen(["/usr/bin/mupdf", self.pdf]).pid


    def get_thumbnail_page(self):
        if self.slide < self.nslides - 1:
            return self.document.get_page(self.slide + 1)
        else:
            return None

class Rehearser(PoorMansPresenterConsole):
    def __init__(self, fn, parent):
        PoorMansPresenterConsole.__init__(self, fn, parent)
        parent.title('Rehearsing {}'.format(self.pdf))

        self.ui_init()

    def get_thumbnail_page(self):
        print 'self.slide: {}; label is {}'.format(self.slide, self.document.get_page(self.slide).get_label())
        return self.document.get_page(self.slide)

    def set_note(self):
        self.note.set('Rehearsing {}/{}: '.format(self.slide + 1, self.nslides) +
                      self.notes[self.index_to_note_num[self.slide]])

def main():
    root = Tkinter.Tk()
    root.geometry("1024x600+100+100")
    if 'rehearse' in sys.argv[0]:
        print 'rehearsing!'
        Thing = Rehearser
    else:
        print 'presenting!'
        Thing = Presenter
    app = Thing(sys.argv[1], root)
    root.mainloop()  

if __name__ == '__main__':
    main()  
