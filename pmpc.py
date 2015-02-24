"""
display speaker notes

use poppler to render the pages

+/- keys to adjust text size

make text white on dark gray background

forward/back keys: j/k, left/right, up/down, pageup/pagedn, space, maybe
home/end for first/last

drive evince with subprocess running xdotool
"""

# https://docs.python.org/2/library/xml.etree.elementtree.html#module-xml.etree.ElementTree

import sys
import xml.etree.ElementTree as ET
from collections import defaultdict

def parse_notes(fn):
    ret = defaultdict(lambda: '')

    ret.update((int(note.attrib['slide']), note.text)
               for note in ET.parse(fn).getroot())

    return ret


from Tkinter import Tk, Frame, Checkbutton, Message
from Tkinter import IntVar, BOTH

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
        self.bind_all("<Key>", self.onKeyPressed)
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

    def onKeyPressed(self, e): 
        key = e.keysym
        print key
        # app.msg['text']
        self.msg.pack_forget()
        self.size += 1
        self.msg = Message(self, text="oh my a message", font=("Helvetica", self.size, "bold"))
        self.msg.pack()


def main():
    root = Tk()
    root.geometry("250x150+300+300")
    app = Example(root)
    root.mainloop()  


if __name__ == '__main__':
    main()  
