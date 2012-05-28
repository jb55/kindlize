#!/usr/bin/env python
#Last-modified: 28 May 2012 05:45:27 PM

import os
from os.path import basename, join
from urlparse import urlsplit
from tempfile import mkstemp
import urllib2
import tarfile
import shutil
import re


# directories
saveDir = os.path.expanduser("~/tmp/")
origDir = os.path.expanduser("~/mercurial/kindlize/")
clibDir = os.path.expanduser("~/mercurial/kindlize/clslib/")
dropDir = os.path.expanduser("~/Dropbox/kindle_sync/")


# syle regexp taken directly from arxiv2bib
NEW_STYLE = re.compile(r'\d{4}\.\d{4}(v\d+)?$')
OLD_STYLE = re.compile( r'(astro-ph)' + r'(\.[A-Z]{2})?/\d{7}(v\d+)?$' )

# geometry configuration
kindlestr     = "\usepackage[paperwidth=13.8cm, paperheight=22.0cm, top=0.5cm, left=0.5cm, right=0.5cm, bottom= 0.5cm]{geometry}\n"
kindlestr_apj = "\usepackage[paperwidth=13.8cm, paperheight=22.0cm, top=2.3cm, left=1.5cm, right=0.0cm, bottom=-1.0cm]{geometry}\n"
kindlestr_mn  = "\usepackage[paperwidth=13.8cm, paperheight=22.0cm, top=1.5cm, left=0.5cm, right=0.5cm, bottom= 0.5cm]{geometry}\n"

# latex cls library
jname = { "elsart_mm" : "Elsevier Science",
          "aa"        : "AA",
          "emulateapj": "ApJ",
          "aastex"    : "AAS Preprint",
          "mn2e"      : "MNRAS",
        }

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
    print("as %s" % absFileName)
    f = open(absFileName, 'wb')
    f.write(r.read())
    f.close()
    return(absFileName)

def unTarAndModify(filename, year):
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
    bstfiles = []
    bblfiles = []
    for file in os.listdir(desdir) :
        if file.endswith(".tex") :
            print("found tex file in the tar bundle %s" % file)
            texfiles.append(file)
        elif file.endswith(".cls") :
            print("found cls file in the tar bundle %s" % file)
            clsfiles.append(file)
        elif file.endswith(".bst") :
            print("found bst file in the tar bundle %s" % file)
            bstfiles.append(file)
        elif file.endswith(".bbl") :
            print("found bbl file in the tar bundle %s" % file)
            bblfiles.append(file)
#   go through all files
    masterfile = None
    for texfile in texfiles :
        texfile = os.path.join(desdir, texfile)
        if 'documentclass' in open(texfile).read():
            # make sure master file is main.tex
            masterfile = os.path.join(desdir, "main.tex")
            shutil.move(texfile, masterfile)
    if masterfile :
        print("master tex file is %s"%masterfile)
    else :
        print("missing master tex file or stone-age tex version?")
        return(None)
    # copy bbl if there is one and only one such file
    if len(bblfiles) == 1 :
        # make sure this works
        print("copying bbl file")
        bblfile_old = os.path.join(desdir, bblfiles[0])
        bblfile_new = os.path.join(desdir, "main.bbl")
        shutil.move(bblfile_old, bblfile_new)
#   play with master file
    classname   = None
    classoption = None
    firstauthor = None
    f = open(masterfile, "r")
    p = re.compile("[^\%]documentclass(.*)\{(\w+)\}")
    q = re.compile("[^\%]author\{([\w|\s|\.|\~]+)")
    q_mn = re.compile("[^\%]author\[[\w|\s|\.|\~]*\]\{([\w|\s|\.|\~]+)")
    for line in f.readlines():
        presult = p.match(line)
        qresult = q.match(line)
        qresult_mn = q_mn.match(line)
        if presult :
            classoption = presult.group(1)
            classname   = presult.group(2)
        if qresult : 
            firstauthor = qresult.group(1)
        elif qresult_mn :
            firstauthor = qresult_mn.group(1)
    if classname :
        print("documentclass is %s"% classname)
    else :
        print("missing classname?")
        return(None)
    # make sure the cls file exist
    clsfile = ".".join([classname, "cls"])
    if not (clsfile in clsfiles) :
        print("%s needed"%clsfile)
        if file_exists(os.path.join(clibDir, clsfile)):
            shutil.copy(os.path.join(clibDir, clsfile), desdir)
        else :
            print("failed to find it in the cls library")
            return(None)
    bstfile = ".".join([classname, "bst"])
    if not (bstfile in bstfiles) :
        if file_exists(os.path.join(clibDir, bstfile)):
            shutil.copy(os.path.join(clibDir, bstfile), desdir)
        else :
            print("probably the references will be messed up")

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
    if firstauthor :
        firstauthor = firstauthor.replace("~", " ")
        author = firstauthor.split()[-1]
    else :
        author = "unknown"
    # parse class
    col_set, onecol_arg, twocol_arg = parse_documentclass(classname, classopts)
    # substitute
    kindlizeit(masterfile, hasoptbracket, classname, col_set, onecol_arg, twocol_arg)
    # recompile
    pdfout = do_latex(desdir, masterfile)
    # rename
    newpdfname = author + year + ".pdf"
    newpdf = os.path.join(desdir, newpdfname)
    shutil.move(pdfout, newpdf)
    return(newpdf)
   
def dropit(pdf) :
    shutil.copy(pdf, dropDir)

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


def kindlizeit(masterfile, hasoptbracket, classname, col_set, onecol_arg, twocol_arg):
    if col_set == "one" :
        pass
    elif col_set == "two" :
        if onecol_arg is not None :
            replaceAll(masterfile, twocol_arg, onecol_arg)
        else :
            print("Nothing I can do about, stay with twocolumn")
    elif col_set == "default" :
        if onecol_arg is not None :
            if hasoptbracket :
                print("adding %s into brackets"%onecol_arg)
                replaceAll(masterfile, "documentclass[", "documentclass["+onecol_arg+",")
            else :
                print("adding %s and brackets"%onecol_arg)
                replaceAll(masterfile, "documentclass", "documentclass["+onecol_arg+"]")
        else :
            print("Nothing I can do about, stay with default, maybe you are lucky")
    # add kindlestr 
    p = re.compile(r"^\\begin{document}")
    if classname == "emulateapj" :
        subst = kindlestr_apj+r"\\begin{document}"
    elif classname == "mn2e" :
        subst = kindlestr_mn+r"\\begin{document}"
    else :
        subst = kindlestr+r"\\begin{document}"
    substituteAll(masterfile, p, subst)
    # comment out hyperref
    p = re.compile("[^\%]usepackage(.*)\{hyperref\}")
    commentALL(masterfile, p)


def parse_documentclass(classname, classopts):
    col_set = "default"
    if (classname == "elsart_mm" or classname == "aa" or classname ==
    "emulateapj" or classname == "aastex" or classname == "mn2e") :
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
        print("the existing file uses default column settting")

    return(col_set, onecol_arg, twocol_arg)
        

def substituteAll(file, pattern, subst):
    #Create temp file
    fh, abs_path = mkstemp()
    new_file = open(abs_path,'w')
    old_file = open(file)
    for line in old_file:
        if re.search(pattern, line):
            print("find pattern in %s"%line)
            new_file.write(re.sub(pattern, subst, line))
        else :
            new_file.write(line)
    #close temp file
    new_file.close()
    os.close(fh)
    old_file.close()
    #Remove original file
    os.remove(file)
    #Move new file
    shutil.move(abs_path, file)

def replaceAll(file, pattern, subst):
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

def commentALL(file, pattern):
    #Create temp file
    fh, abs_path = mkstemp()
    new_file = open(abs_path,'w')
    old_file = open(file)
    for line in old_file:
        if pattern.match(line):
            new_file.write(r"%" + line)
        else :
            new_file.write(line)
    #close temp file
    new_file.close()
    os.close(fh)
    old_file.close()
    #Remove original file
    os.remove(file)
    #Move new file
    shutil.move(abs_path, file)

def parse_args():
    import argparse
    parser = argparse.ArgumentParser(
      description="""Kindlize pdfs from astro-ph""")
    parser.add_argument('id',metavar='arxiv_id',
      help="arxiv identifier, such as 1008.0641")
    return(parser.parse_args())

def getTar(arxivid):
    chkres = is_new(arxivid)
    if chkres is True :
        url  = "".join(["http://arxiv.org/e-print/", arxivid])
        year = arxivid[0:2]
    elif chkres is False :
        num = arxivid.split("/")[-1]
        year = num[0:2]
        url = "".join(["http://arxiv.org/e-print/astro-ph/", num])
    else :
        raise RuntimeError("invalid id, please check your input")
    print("downloading source from %s" % url)
    fname = download(url=url)
    return(fname, year)

def is_new(id):
    """
    Checks if id is a new arxiv identifier
    http://arxiv.org/help/arxiv_identifier_for_services
    """
    if NEW_STYLE.match(id) is not None :
        return(True)
    elif OLD_STYLE.match(id) is not None:
        return(False)
    else :
        return(None)




if __name__ == '__main__':
    args = parse_args()
    arxivid = args.id
    fname, year  = getTar(arxivid)
    newpdf = unTarAndModify(fname, year)
    if newpdf :
        os.system("evince "+newpdf)
    dropit(newpdf)


    


