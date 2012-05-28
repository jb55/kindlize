#!/usr/bin/env python
#Last-modified: 28 May 2012 02:21:47 AM

from tempfile import mkstemp
import os
from os.path import basename, join
import shutil
from urlparse import urlsplit
import urllib2
import tarfile
import re

saveDir = "/home/nye/tmp/"
origDir = "/home/nye/mercurial/kindlize/"

def url2name(url):
    return(basename(urlsplit(url)[2]))

def download(url):
    localName = url2name(url)
    req = urllib2.Request(url)
    r = urllib2.urlopen(req)
    if r.info().has_key('Content-Disposition'):
        # If the response has Content-Disposition, we take file name from it
        localName = r.info()['Content-Disposition'].split('filename=')[1]
        if localName[0] == '"' or localName[0] == "'":
            localName = localName[1:-1]
    elif r.url != url: 
        # if we were redirected, the real file name we take from the final URL
        localName = url2name(r.url)

    # get it to a default directory
    if saveDir is not None:
        absFileName = join(saveDir, localName)
    else:
        absFileName = localName

#    absFileName = absFileName + ".pdf"

    print("as %s" % absFileName)
    f = open(absFileName, 'wb')
    f.write(r.read())
    f.close()

    return(absFileName)

def unTarAndModify(filename):
    try :
        print('%20s  is a tar file? %s \n continue' % (filename, tarfile.is_tarfile(filename)))
    except IOError, err :
        print('%20s  is a tar file? %s \n exiting' % (filename, err))
        return(None)
    t = tarfile.open(filename, 'r')
    desdir = os.path.join(saveDir, "outdir")
    if os.path.exists(desdir):
        shutil.rmtree(desdir)
    else:
        pass
    #
    try :
        os.mkdir(desdir)
    except OSError, err :
        print("mkdir %s failed, %s"%(desdir, err))
        return(None)
    # extract tar
    t.extractall(desdir)
    texfiles = []
    clsfiles = []
#    for file in t.getnames() :
    for file in os.listdir(desdir) :
        if file.endswith(".tex") :
            print("found tex file in the tar bundle %s" % file)
            texfiles.append(file)
        elif file.endswith(".cls") :
            print("found cls file in the tar bundle %s" % file)
            clsfiles.append(file)
#   go through tex and cls files
    masterfile = None
    for texfile in texfiles :
        texfile = os.path.join(desdir, texfile)
        if 'documentclass' in open(texfile).read():
            masterfile = texfile
    if masterfile :
        print("master tex file is %s"%masterfile)
    else :
        print("missing master tex file?")
        return(None)
#   play with master file
    classname   = None
    classoption = None
    f = open(masterfile, "r")
    p = re.compile("[^\%]documentclass(.*)\{(\w+)\}")
    for line in f.readlines():
        result = p.match(line)
        if result :
            classoption = result.group(1)
            classname   = result.group(2)
    if classname :
        print("documentclass is %s"% classname)
    else :
        print("missing classname?")
        return(None)
    if classoption :
        classopts = classoption.lstrip("[").rstrip("]").split(",")
        if len(classopts) == 0 :
            print("empty class options")
            hasoptbracket = True
        else :
            print(classopts)
            hasoptbracket = True
    else :
        classopts = []
        hasoptbracket = False
        print("no class options")
    # parse class
    col_set, onecol_arg, twocol_arg = parse_documentclass(classname, classopts)
    # substitute
    kindlizeit(masterfile, hasoptbracket, classname, col_set, onecol_arg, twocol_arg)
    # recompile
    pdfout = do_latex(desdir, masterfile)
    return(pdfout)
    

def do_latex(desdir, masterfile) :
    mkfile = os.path.join(origDir, "Makefile_latex")
    shutil.copy(mkfile, os.path.join(desdir, "Makefile"))
    cwd = os.getcwd() # get current directory
    os.chdir(desdir)
    try:
        os.system("make")
    finally:
        os.chdir(cwd)
    pdfout = os.path.join(desdir, masterfile.replace(".tex", ".pdf"))
    if file_exists(pdfout):
        print("sucessfully generated kindle pdf")
        return(pdfout)
    else :
        print("failed to generate kindle pdf")
        return(None)

def file_exists(file):
    try:
        f = open(file, "r")
        f.close()
        return(True)
    except :
        return(False)

kindlestr = "\usepackage[paperwidth=13.8cm, paperheight=22.0cm, top=0.5cm, left=0.5cm, right=0.5cm, bottom=0.5cm]{geometry}\n"


def kindlizeit(masterfile, hasoptbracket, classname, col_set, onecol_arg, twocol_arg):
    if col_set == "one" :
        pass
    elif col_set == "two" :
        if onecol_arg is not None :
            replace(masterfile, twocol_arg, onecol_arg)
        else :
            print("Nothing I can do about, stay with twocolumn")
    elif col_set == "default" :
        if onecol_arg is not None :
            if hasoptbracket :
                print("adding %s into brackets"%onecol_arg)
                replace(masterfile, "documentclass[", "documentclass["+onecol_arg+",")
            else :
                print("adding %s and brackets"%onecol_arg)
                replace(masterfile, "documentclass", "documentclass["+onecol_arg+"]")
        else :
            print("Nothing I can do about, stay with default, maybe you are lucky")
    # add kindlestr
    replace(masterfile, r"\begin{document}", kindlestr+r"\begin{document}")


jname = { "elsart_mm" : "Elsevier Science",
          "aa"        : "AA",
        }

def parse_documentclass(classname, classopts):
    col_set = "default"
    if classname == "elsart_mm" or classname == "aa" :
        print("Journal Name: %20s"%jname[classname])
        print("`one/twocolumn` option is available")
        onecol_arg = "onecolumn"
        twocol_arg = "twocolumn"
        if onecol_arg in classopts :
            col_set = "one"
        elif twocol_arg in classopts :
            col_set = "two"
#    elif classname == "aa" :
#        print("Journal Name: AA")
    else :
        raise RuntimeError("unknown documentclass, please update library")

    if col_set == "one":
        print("`onecolumn` enabled")
    elif col_set == "two":
        print("`twocolumn` enabled")
    else :
        print("the existing file uses default columne settting")

    return(col_set, onecol_arg, twocol_arg)
        


def replace(file, pattern, subst):
    #Create temp file
    fh, abs_path = mkstemp()
    new_file = open(abs_path,'w')
    old_file = open(file)
    for line in old_file:
        new_file.write(line.replace(pattern, subst))
    #close temp file
    new_file.close()
    os.close(fh)
    old_file.close()
    #Remove original file
    os.remove(file)
    #Move new file
    shutil.move(abs_path, file)





if __name__ == '__main__':
    import sys
    arxivid = sys.argv[1]
    url = "".join(["http://arxiv.org/e-print/", arxivid])
    print("downloading source from %s" % url)
    fname = download(url=url)
    pdfout = unTarAndModify(fname)
    if pdfout :
        os.system("mupdf2 "+pdfout)


    


