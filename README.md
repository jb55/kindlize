
Kindlize
========

Tired and/or guilty of printing out arXiv pre-prints everyday? Frustrated by
the experience of reading two-column journal articles on your e-reader?

If you happen to own a [Kindle
DX](http://www.amazon.com/Kindle-DX-Wireless-Reader-3G-Global/dp/B002GYWHSQ)
device, and happen to be an avid [arXiv](http://arxiv.org/) reader, Kindlize
will make reading arXiv pre-prints on e-ink screen as pleasant as on A4 papers!

The idea is simple. arXiv usually keeps the LaTeX source file of uploaded
manuscripts, and Kindlize will reformat and recompile those LaTeX files so
that the new pdf file is Kindlie-friendly.


Screenshots
-----------

### Before (pure text and equations)

[![Screenshot](http://bitbucket.org/nye17/kindlize/raw/default/screenshots/textpage_before_small_framed.png)](http://bitbucket.org/nye17/kindlize/raw/default/screenshots/textpage_before.png)


### After (pure text and equations)

![Screenshot](http://bitbucket.org/nye17/kindlize/raw/default/screenshots/textpage_after_small_framed.png)


### Before (with Figure)

![Screenshot](http://bitbucket.org/nye17/kindlize/raw/default/screenshots/figpage_before_small_framed.png)

### After (with Figure)

![Screenshot](http://bitbucket.org/nye17/kindlize/raw/default/screenshots/figpage_after_small_framed.png)



Configuration
-------------

Kindlize reads a configuratoin file under your home directory
`~/.kindle.cfg` to process the pdf files and connect to your Kindle device.

### tmpDir=~/tmp

Determines where the TeX file will be unpacked and compiled into pdfs.

### dropDir=~/Dropbox/kindle_sync/

Determines where on your local directory you want to store a backup of your Kindle arixv-related direcotry.

### incomingDir=/media/Kindle/documents/Incoming/

Tells Kindlize where your Kindle content will show up in your file system and which subdirectory should you store the arXiv files.


Contributing
------------

Please, report bugs and issues as I won't be able to cover all the TeX formats on arXiv. Feel free to send me ideas through the [issue tracker][] or pull requests!

[issue tracker]: http://github.com/nye17/kindlize/issues
