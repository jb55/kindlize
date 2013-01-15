
Kindlize
========

A color scheme for Vim, pieced together by [Steve Losh](http://stevelosh.com/).

There's still quite a lot of room for improvement (particularly in HTML) so feel
free to send me ideas through the [issue tracker][] or pull requests.


[issue tracker]: http://github.com/nye17/kindlize/issues

Screenshots
-----------


### Before

![Screenshot](http://i.imgur.com/fQGGC.png)

### After

![Screenshot](http://i.imgur.com/LgLar.png)


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

Please, report bugs and issues as I won't be able to cover all the TeX formats on arXiv!
