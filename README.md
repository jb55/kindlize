
Kindlize
========

Changelog
---------

### 0.1.0 ###

    * 07 May 2013: fixed several packaging errors in previous tar balls.


Introduction
------------

Tired and/or guilty of printing out arXiv pre-prints everyday? Frustrated by
the experience of reading two-column journal articles on your Kindle e-reader?

If you happen to own a [Kindle
DX](http://www.amazon.com/Kindle-DX-Wireless-Reader-3G-Global/dp/B002GYWHSQ)
device, and happen to be an avid [arXiv](http://arxiv.org/) reader, Kindlize
will make reading arXiv pre-prints on e-ink screen as pleasant as on A4 papers!

The idea is simple. arXiv usually keeps the LaTeX source file of uploaded
manuscripts, and Kindlize will reformat and recompile those LaTeX files so
that the new pdf file is Kindle-friendly.

_CAVEAT_

Currently Kindlize only works with `astro-ph` posts on arXiv, but it could
be easily adapted to other fields by adding LaTeX style files for relevant
journals. Please let me know if you want to work on implementing Kindlize
for fields outside of Astrophysics.




Screenshots
-----------

### Before (pure text and equations)

![Screenshot](http://bitbucket.org/nye17/kindlize/raw/default/screenshots/textpage_before_small_framed.png)


### After (pure text and equations)

![Screenshot](http://bitbucket.org/nye17/kindlize/raw/default/screenshots/textpage_after_small_framed.png)


### Before (with Figure)

![Screenshot](http://bitbucket.org/nye17/kindlize/raw/default/screenshots/figpage_before_small_framed.png)

### After (with Figure)

![Screenshot](http://bitbucket.org/nye17/kindlize/raw/default/screenshots/figpage_after_small_framed.png)


Requirements
------------

* python2.7
* a LaTeX environment
* rsync
* [Dropbox](http://db.tt/i5xwlaj9) (suggested)
* GNU Make


Installation
------------

If you have [mercurial](http://mercurial.selenic.com) installed, clone
the source

    $ hg clone ssh://hg@bitbucket.org/nye17/kindlize 

otherwise you can download tarball from
[here](https://bitbucket.org/nye17/kindlize/downloads), then
    
    $ tar zxvf kindlize-0.1.0.tar.gz

to de-compress under your current directory.

To install,

    $ cd kindlize
    $ python setup.py install

or if you want to install to a specified directory `INSTALLDIR`

    $ python setup.py install --prefix=INSTALLDIR


Workflow
--------

It is useful to explain the ideal workflow using Kindlize. There are three
major goals I want to achieve for a hassle-free reading experience:

* Converting the source tarball downloaded from arXiv server into Kindle-friendly pdf for any arXiv-id.
* Maintaining a local directory of "kindlized" pdfs among multiple computers (using Dropbox).
* Synchronizing your Kindle arXiv content to the local directory on your computer. 

Kindlize is designed to take care of all three goals, with some help from
Dropbox (simply by storing your local copy of kindlized pdfs inside your
Dropbox directory).

However, before typing `kindlize` on your terminal, you need to configurate
Kindlize first. Let's get started!


Configuration
-------------

Obviously, Kindlize needs to understand the filesystems of both your computer
and Kindlize device - like, where to put temporary files during compiling, where
to put kindlized pdfs on your computer and on your Kindle, etc. For this
purpose, Kindlize needs to read a configuration file under your home directory
`~/.kindle.cfg`. You can modify the `example.cfg` file that comes with the
source package and copy it to your local home directory,

    $ copy example.cfg ~/.kindle.cfg

and tailor it to your own needs. The required items in `~/.kindle.cfg` are

## [general]

### device=Kindle DX

Currently Kindlize only serves the Kindle DX device, as other Kindle versions
are too small for serious journal reading. But if you want to give it a shot,
please let me know (I don't personally own other Kindles, so I may need your
help on tests).

## [directory]

### tmpDir=~/tmp

Determines where the TeX file will be unpacked and compiled into pdfs. A
standard `tmp` directory would be ideal.

### dropDir=~/Dropbox/kindle_sync/

Determines where on your local directory you want to store a backup of your
Kindlized pdfs. Here I put it as a subdirectry within my Dropbox folder,
so that I could select and process the desired pdfs on my office machine,
then sync and update my Kindle using my home computer later. You need to
create `dropDir` on your computer manually.

### mountDir=/media/Kindle/

The mount point of your Kindle device. You have to make sure that `mountDir` is
writable by your user account.

### incomingDir=/media/Kindle/documents/Incoming/

Tells Kindlize where your Kindle content will show up in your file system
(i.e., the `/media/Kindle` part, which should be the same as `mountDir`) 
and which subdirectory you want to store the
arXiv files (i.e., the `documents/Incoming` part). Note that `incomingDir`
will always be synced to `dropDir`. You also need to create `incomingDir`
on your Kindle manually.

## [LaTeX]

### font=charter

Determines which LaTeX font package to use for pdfs. You have
to make sure they are available in your LaTeX environment - place
`\usepackage{YOUR_CHOICE_OF_FONT}` in your test LaTeX file and compile.

### fontheight=14pt

Determines the height of your fonts.

### fontwidth=18pt

Determines the baseline of your fonts.

## [pdf]

### pdfviewer=mupdf

Determines which pdf viewer to preview the generated pdfs on your computer. `mupdf` is
strongly recommended.
 

Usage
-----

To kindlize an arXiv article, simply do

    $ kindlize 1211.1379 astrocoffee

where [`1211.1379`](http://arxiv.org/abs/1211.1379) is the arXiv identifier for
the paper you want to read, and `astrocoffee` is the name of the subdirectory
you want to keep this file under your `dropDir` and `incomingDir`. If you
don't want to bother with organizing your pdfs, simply substitute `astrocoffee`
with `.`.

As indicated by `example.cfg`, I have created a local directory
`~/Dropbox/kindle_sync/` as my `dropDir` for storing kindlized pdfs, so that
the reformated pdf (turns out to be, _accidentally_, `Zu12.pdf`) will go into
`~/Dropbox/kindle_sync/astrocoffee` directory.

The above command will also enable you to preview the kindlized pdf using
your favorite `pdfviewer`.

I have also created a new directory under Kindle `documents/incoming/` as my
`incomingDir` to synchronize to the `~/Dropbox/kindle_sync/` directory on
my computer. To synchronize, simply plug in your Kindle and make sure that
the Kindle filesystem is accessible (e.g., in my case, `/media/Kindle/`
exists.), then run

    $ kindlize

without arguments. This will force the Kindle `incomingDir` directory to
be exactly the same as your local `dropDir` directory (i.e., files could
be either added or deleted from your Kindle!). This command will also send
the newly added pdfs to the right `collection` on your Kindle. For example,
`Zu12.pdf` file will appear in the `incoming - astrocoffee` collection,
however, you have to reboot your Kindle to see the new `collection` in action ;-(.


You can always type

    $ kindlize -h

for help.


And last, enjoy reading!


Contributing
------------

Please, report bugs and issues as I won't be able to cover all the TeX
formats on arXiv. Feel free to send me ideas through the [issue tracker][]
or pull requests!

[issue tracker]: http://bitbucket.org/nye17/kindlize/issues
