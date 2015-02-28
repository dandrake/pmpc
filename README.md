# pmpc

poor man's presenter console -- a sort of spork of
[pdf-presenter-console](https://github.com/davvil/pdfpc). It's not a
fork, it's a...spork.

Intended for presentations with a laptop and projector, with one screen
being projected and another with speaker notes and slide previews.

This program utilizes an advanced software engineering technique called
Make The User Do It. To actually present the PDF, it spans `mupdf`. Want
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

# ideas, todo

put all the LaTeX support stuff in a .sty file

just do GTK? Then Python 3 works: http://stackoverflow.com/a/9694048
