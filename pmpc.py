"""display speaker notes

use poppler to render the pages

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

colors stolen from http://ethanschoonover.com/solarized


"""

# https://docs.python.org/2/library/xml.etree.elementtree.html#module-xml.etree.ElementTree

import sys
import os.path
import xml.etree.ElementTree as ET
from collections import defaultdict
from Tkinter import Tk, Frame, Checkbutton, Message, Label
from Tkinter import IntVar, BOTH, LEFT, RIGHT, Y
import Tkinter
import PIL.ImageTk
import PIL.Image
from cairo import ImageSurface, Context, FORMAT_ARGB32
import subprocess
import poppler

def parse_notes(fn):
    ret = defaultdict(lambda: '')
    try:
        ret.update((int(note.attrib['slide']), note.text)
                   for note in ET.parse(fn).getroot())
    except IOError:
        ret[0] = 'no file {}!'.format(fn)
    return ret

class Presenter(Frame):
    def __init__(self, fn, parent):
        self.fn = os.path.splitext(fn)[0]
        self.notes = parse_notes(self.fn + '.notes.xml')
        self.pdf = self.fn + '.pdf'
        self.slide = 0
        self.document = poppler.document_new_from_file('file://' + os.path.abspath(self.pdf), None)
        self.nslides = self.document.get_n_pages()
        self.current_page = self.document.get_page(self.slide + 1)
        self.slide_size = tuple(int(_) for _ in self.current_page.get_size())
        #self.mupdf_pid = subprocess.Popen(["/usr/bin/mupdf", self.pdf]).pid

        self.nextkeys = ['j', 'J', 'Right', 'Down', 'Next', 'space']
        self.prevkeys = ['k', 'K', 'Left', 'Up', 'Prior', 'BackSpace']
        # store digits so you can re-sync slides & pdf
        self.digits = ''

        Frame.__init__(self, parent, background='#002b36')
        self.parent = parent
        self.textsize = 20

        self.parent.title('Presenting {}'.format(self.pdf))

        self.notes[0] = "\nDo 'f', then 'H' to fullscreen mupdf.\n" + self.notes[0]
        self.note = Message(self, text="{}/{}:".format(self.slide + 1, self.nslides) + self.notes[0], font=('Helvetica', self.textsize, 'bold'), background='#008800')

        self.surface = ImageSurface(FORMAT_ARGB32, self.slide_size[0], self.slide_size[1])
        self.context = Context(self.surface)
        self.current_page.render(self.context)
        self._image_ref = PIL.ImageTk.PhotoImage(PIL.Image.frombuffer("RGBA", self.slide_size, self.surface.get_data(), "raw", "BGRA", 0, 1))
        self.label = Label(self, image=self._image_ref)
        self.label.pack()

        self.shownote()
        self.focus_get()
        self.bind_all("<Key>", self.onKeyPressed)
        
    def shownote(self):
        print 'width:', self.winfo_width()
        self.note.pack_forget()
        self.note = Message(self, text='{}/{}:\n'.format(self.slide + 1, self.nslides) + self.notes[self.slide], font=('Helvetica', self.textsize, 'bold'), background='#002b36', fg='#eee8d5', width=500, anchor='nw')
        self.note.pack(side=LEFT, fill=BOTH, anchor='nw', expand=1)

        if self.slide < self.nslides - 1:
            self.current_page = self.document.get_page(self.slide + 1)
            self.current_page.render(self.context)
            self._image_ref = PIL.ImageTk.PhotoImage(PIL.Image.frombuffer("RGBA", self.slide_size, self.surface.get_data(), "raw", "BGRA", 0, 1))
            self.label.pack_forget()
            self.label = Label(self, image=self._image_ref)
            self.label.pack(side=RIGHT, anchor='n')
        else:
            # no slide to preview...don't display anything
            self.label.pack_forget()
        self.pack(fill=BOTH, expand=1)

    def onKeyPressed(self, e): 
        key = e.keysym
        print key
        if key == 'plus':
            self.textsize += 3
            self.shownote()
        if key == 'minus':
            self.textsize -= 3
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

def main():
    root = Tk()
    root.geometry("800x600+100+100")
    app = Presenter(sys.argv[1], root)
    root.mainloop()  

if __name__ == '__main__':
    main()  

