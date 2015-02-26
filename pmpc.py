"""
display speaker notes

use poppler to render the pages

+/- keys to adjust text size

make text white on dark gray background

forward/back keys: j/k, left/right, up/down, pageup/pagedn, space, maybe
home/end for first/last

drive evince with subprocess running xdotool

http://zetcode.com/gui/tkinter/widgets/

nope, let's do mupdf; evince seems to not listen to keypresses when the window isn't focused (as will always be the case here), but mupdf does.

"""

# https://docs.python.org/2/library/xml.etree.elementtree.html#module-xml.etree.ElementTree

import sys
import os.path
import xml.etree.ElementTree as ET
from collections import defaultdict
from Tkinter import Tk, Frame, Checkbutton, Message
from Tkinter import IntVar, BOTH
import subprocess


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
        self.mupdf_pid = subprocess.Popen(["/usr/bin/mupdf", self.pdf]).pid
        print 'my fn is', self.fn
        print 'my notes are' , self.notes
        # FIXME get number of pages

        self.nextkeys = ['j', 'J', 'Right', 'Down', 'Next', 'space']
        self.prevkeys = ['k', 'K', 'Left', 'Up', 'Prior'] # backspace

        Frame.__init__(self, parent)
        self.parent = parent
        self.textsize = 20

        # could get pdf title via poppler?
        self.parent.title('Presenting {}.pdf'.format(fn))

        self.note = Message(self, text='{}:\n'.format(self.slide), font=('Helvetica', self.textsize, 'bold'))
        self.shownote()
        self.focus_get()
        self.bind_all("<Key>", self.onKeyPressed)

    def shownote(self):
        self.note.pack_forget()
        self.note = Message(self, text='{}:\n'.format(self.slide) + self.notes[self.slide], font=('Helvetica', self.textsize, 'bold'))
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
        if key in self.nextkeys:
            self.slide += 1
            # no spaces in args, so okay to just .split()
            subprocess.call('/usr/bin/xdotool search mupdf key Next'.split())
            self.shownote()
        if key in self.prevkeys and self.slide > 0:
            self.slide -= 1
            subprocess.call('/usr/bin/xdotool search mupdf key Prior'.split())
            self.shownote()

def main():
    root = Tk()
    root.geometry("250x150+300+300")
    #app = Example(root)
    app = Presenter(sys.argv[1], root)
    root.mainloop()  


if __name__ == '__main__':
    main()  

