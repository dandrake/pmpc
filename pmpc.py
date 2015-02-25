"""
display speaker notes

use poppler to render the pages

+/- keys to adjust text size

make text white on dark gray background

forward/back keys: j/k, left/right, up/down, pageup/pagedn, space, maybe
home/end for first/last

drive evince with subprocess running xdotool

http://zetcode.com/gui/tkinter/widgets/


"""

# https://docs.python.org/2/library/xml.etree.elementtree.html#module-xml.etree.ElementTree

import sys
import os.path
import xml.etree.ElementTree as ET
from collections import defaultdict
from Tkinter import Tk, Frame, Checkbutton, Message
from Tkinter import IntVar, BOTH

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
        print 'my fn is', self.fn
        print 'my notes are' , self.notes
        # FIXME get number of pages

        self.nextkeys = ['j', 'J', 'Right', 'Down', 'Next', 'Space']
        self.prevkeys = ['k', 'K', 'Left', 'Up', 'Prior'] # backspace

        Frame.__init__(self, parent)
        self.parent = parent
        self.textsize = 20

        # could get pdf title via poppler?
        self.parent.title('Presenting {}.pdf'.format(fn))

        self.shownote()
        self.focus_get()
        self.bind_all("<Key>", self.onKeyPressed)

    def shownote(self):
        self.msg.pack_forget()
        self.note = Message(self, text=self.notes[self.slide], font=('Helvetica', self.textsize, 'bold'))
        # the pack stuff is dangerously close to cargo cult programming...gotta understand this
        self.note.pack()
        self.pack(fill=BOTH, expand=1)

    def onKeyPressed(self, e): 
        key = e.keysym
        print key
        if key == '+':
            self.size += 3
            self.shownote()
        if key == '-':
            self.size -= 3
            self.shownote()
        if key in self.nextkeys():
            self.slide += 1
            # FIXME also advanced evince and redo preview
            self.shownote()
        if key in self.prevkeys() and self.slide > 0:
            self.slide -= 1
            self.shownote()

class Example(Frame):
  
    def __init__(self, parent):
        Frame.__init__(self, parent)   
         
        self.parent = parent        
        self.initUI()
        
    def initUI(self):
      
        self.parent.title("Checkbutton")

        self.size = 20

        self.msg = Message(self, text="oh my a message", font=("Helvetica", self.size, "bold"))
        self.msg.pack()

        self.pack(fill=BOTH, expand=1)
        self.var = IntVar()
        
        self.focus_get()
        
        # cb = Checkbutton(self, text="Show title",
        #     variable=self.var, command=self.onClick)
        # cb.select()
        # cb.place(x=50, y=50)


#        msg.select()
        
        

    # def onClick(self):
       
    #     if self.var.get() == 1:
    #         self.master.title("Checkbutton")
    #     else:
    #         self.master.title("")

 

def main():
    root = Tk()
    root.geometry("250x150+300+300")
    app = Example(root)
    root.mainloop()  


if __name__ == '__main__':
    #main()  
    Presenter(sys.argv[1])
