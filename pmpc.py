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
"""

# https://docs.python.org/2/library/xml.etree.elementtree.html#module-xml.etree.ElementTree

import sys
import os.path
import xml.etree.ElementTree as ET
from collections import defaultdict
from Tkinter import Tk, Frame, Checkbutton, Message, Label
from Tkinter import IntVar, BOTH
import PIL
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

def get_n_pages(fn):
    return poppler.document_new_from_file('file://' + os.path.abspath(fn), None).get_n_pages()

class Presenter(Frame):
    def __init__(self, fn, parent):
        self.fn = os.path.splitext(fn)[0]
        self.notes = parse_notes(self.fn + '.notes.xml')
        self.pdf = self.fn + '.pdf'
        self.slide = 0
        self.nslides = get_n_pages(self.pdf)
        self.mupdf_pid = subprocess.Popen(["/usr/bin/mupdf", self.pdf]).pid
        #print 'my fn is', self.fn
        #print 'my notes are' , self.notes

        self.nextkeys = ['j', 'J', 'Right', 'Down', 'Next', 'space']
        self.prevkeys = ['k', 'K', 'Left', 'Up', 'Prior', 'BackSpace']
        # store 
        self.digits = ''

        Frame.__init__(self, parent)
        self.parent = parent
        self.textsize = 20

        # could get pdf title via poppler?
        self.parent.title('Presenting {}.pdf'.format(fn))

        self.notes[0] = "\nDo 'f', then 'H' to fullscreen mupdf.\n" + self.notes[0]
        self.note = Message(self, text="{}:".format(self.slide + 1) + self.notes[0], font=('Helvetica', self.textsize, 'bold'))
        self.shownote()
        self.focus_get()
        self.bind_all("<Key>", self.onKeyPressed)

    def shownote(self):
        self.note.pack_forget()
        self.note = Message(self, text='{}:\n'.format(self.slide + 1) + self.notes[self.slide], font=('Helvetica', self.textsize, 'bold'))
        # the pack stuff is dangerously close to cargo cult programming...gotta understand this
        self.note.pack()
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
            

def main():
    root = Tk()
    root.geometry("250x150+300+300")
    #app = Example(root)
    app = Presenter(sys.argv[1], root)
    root.mainloop()  


if __name__ == '__main__':
    main()  

