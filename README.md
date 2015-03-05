# pmpc: poor man's presenter console

...a sort of spork of
[pdf-presenter-console](https://github.com/davvil/pdfpc). It's not a
fork, it's a...spork.

Intended for presenting slides in PDF format (particularly those made
with [Beamer](https://en.wikipedia.org/wiki/Beamer_%28LaTeX%29)) with a
laptop and projector, with one screen being projected and another
showing speaker notes and slide previews.

This program utilizes an advanced software engineering technique called
Make The User Do It. To actually present the PDF, it spawns `mupdf`. Want
it on the screen being projected? Make the user move the window there.
Want it fullscreen? Make the user do it. Want the notes window
maximized? You get the idea.

Less flippantly, this means that things will work how you want them to
-- because you're the one doing it. And because we rely on good tools
like `mupdf` and `poppler`, we can be pretty certain that things will
work well.

# dependencies

* Python 2 and Tkinter;
* Pypoppler;
* Python Cairo
* Python Imaging Library
* [mupdf](http://www.mupdf.com/)
* [xdotool](http://www.semicomplete.com/projects/xdotool/)

# key bindings

It's easy enough to read the code and figure it out, but:

* Forward one slide: any of j, J, right arrow, down arrow, page down, space
  bar.
  
* Back one slide: any of k, K, left arrow, up arrow, page up, backspace

* Go to first slide: home. (Last slide: end.)

* Change notes to slide N: "Ng" -- for example, to display the notes for
  slide 12, type "12g". This won't change the PDF viewer; this is for
  re-synchronizing your notes to the viewer if they somehow get
  unsync'ed.

* Quit: Ctrl-W. The PDF viewer will stay; you have to close that
  yourself. (Make The User Do It, remember?)

* Start timer: t. Right now there's no pausing, stopping, counting down,
  etc.

* Increase text size: +. (Decrease is -.)

# format of the notes file

`pmpc` will look for a `.notes.xml` file containing the notes. The file
`example.notes.xml` explains the format, which is simple enough. If
you're not using Beamer or TeX to generate your PDF, it should be
straightforward to generate the file.

The `beamer.tex` file includes code for generating the notes file
straight from TeX.

# overlays / incremental reveal

The usual way to do overlays (or incremental reveal) in a PDF is to
produce a bunch of pages which, well, incrementally reveal their
contents. This means that there is a one-to-many relationship: one note
in your .tex file should correspond to many pages in the PDF.
Fortunately, Beamer (and, one hopes, any other reasonable system for
producing such PDFs) produces PDFs whose page labels make this structure
figure-out-able and `pmpc` displays the note for all pages of the PDF
corresponding to a single frame (in Beamer parlance).

Right now there is no support for notes that only appear for some
overlays and not others.

# ideas, todo

combine multiple <note> elements with the same slide attribute

put all the LaTeX support stuff in a .sty file

allow multiple <note>s for a single slide, which we'll concatenate.
This'll let me automatically put the answers to clicker questions into
the notes.

the notes are in an XML format, so we could style them: change to
fixed-width text, etc. Also, we could use XSLT to transform the notes
into something that would look nice when printed.

Seems like no Python 3 bindings for Poppler, but I think if you use GTK,
you can access Poppler through there: http://stackoverflow.com/a/9694048

...and also embed Evince? https://stackoverflow.com/questions/8942604/embed-evince-python-gi/9067463#9067463
