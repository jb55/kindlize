#!/usr/bin/env python
#Last-modified: 13 Jun 2012 03:32:17 AM
import os
from urlparse import urlsplit
from tempfile import mkstemp
from glob import glob
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
kindlestr_mn  = "\usepackage[paperwidth=13.8cm, paperheight=22.0cm, top=2.5cm, left=0.5cm, right=0.5cm, bottom= 0.5cm]{geometry}\n"
kindlestr_els = "\usepackage[paperwidth=15.8cm, paperheight=22.0cm, top=0.5cm, left=0.5cm, right=0.5cm, bottom= 0.3cm]{geometry}\n"

# font name
fontstr = "\usepackage{charter}\n"

# enbiggen font
magnifystr = "\n"+r"\\fontsize{14pt}{18pt}\selectfont"+"\n"

# latex cls library
jname = { "elsart_mm" : "Elsevier Science",
          "aa"        : "AA",
          "emulateapj": "ApJ",
          "aastex"    : "AAS Preprint",
          "mn2e"      : "MNRAS",
          "article"   : "Generic Article",
          "elsarticle": "Elsevier Science",
        }

#banned_packages = ["hyperref", "emulateapj5"]
banned_packages = ["emulateapj5"]

old_files = ["aaspp4.sty", "psfig.sty", "flushrt.sty", "mn.cls"]

class KindleException(Exception):
    pass


def url2name(url):
    return(os.path.basename(urlsplit(url)[2]))

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
        absFileName = os.path.join(saveDir, localName)
    else:
        absFileName = localName
    print("as %s" % absFileName)
    f = open(absFileName, 'wb')
    f.write(r.read())
    f.close()
    return(absFileName)

def findFigs(t, ext="ps"):
    # find all the ps figure files
    figfiles = []
    for file in t.getnames() :
        if file.endswith("."+ext) :
            print("found %s image in the tar bundle %s" % (ext, file))
            figfiles.append(file)
    return(figfiles)

def force_mkdir(desdir):
    if os.path.exists(desdir):
        shutil.rmtree(desdir)
    else :
        try :
            os.mkdir(desdir)
        except OSError, err :
            raise KindleException("mkdir %s failed, %s"%(desdir, err))

def examine_texenv(desdir):
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
    return(texfiles, clsfiles, bstfiles, bblfiles)

def getMaster(texfiles, desdir):
    masterfile = None
    for texfile in texfiles :
        texfile = os.path.join(desdir, texfile)
        content = open(texfile).read()
        if 'documentclass' in content:
            # make sure master file is main.tex
            print("copying main tex file")
            masterfile = os.path.join(desdir, "main.tex")
            shutil.move(texfile, masterfile)
            texversion = "latex2e"
        elif r'\begin{document}' in content:
            # make sure master file is main.tex
            print("copying main tex file, possibly latex2.09 file")
            masterfile = os.path.join(desdir, "main.tex")
            shutil.move(texfile, masterfile)
            texversion = "latex2.09"
    if masterfile is None :
        raise KindleException("missing master tex file or stone-age tex version?")
    return(masterfile, texversion)
            
def getBiblio(bblfiles, desdir):
    # copy bbl if there is one and only one such file
    if len(bblfiles) == 1 :
        # make sure this works
        bblfile_old = os.path.join(desdir, bblfiles[0])
        bblfile_new = os.path.join(desdir, "main.bbl")
        print("copying main bbl file  from %s"% bblfiles[0])
        shutil.copy(bblfile_old, bblfile_new)

def checkMaster(masterfile, texversion) :
    if texversion == "latex2.09" :
        classname   = "old"
        classoption = "old"
        f = open(masterfile, "r")
        q = re.compile("[^\%]author[\[|\]|\w|\s|\.|\~]*\{([\w|\s|\.|\~]+)")
        for line in f.readlines():
            qresult = q.match(line)
            if qresult : 
                firstauthor = qresult.group(1)
                break
        if qresult : 
            author = firstauthor.split()[-1]
        else :
            author = "unknown"
        f.close()
        return(classoption, classname, author)
    classname   = None
    classoption = None
    firstauthor = None
    f = open(masterfile, "r")
    p = re.compile("[^\%]documentclass(.*)\{(\w+)\}")
    q = re.compile("[^\%]author\{([\w|\s|\.|\~]+)")
    q_mn  = re.compile("[^\%]author\[([\w|\s|\.|\~|\\\\|\&]*)\]")
    q_els = re.compile("[^\%]author\[[\d|\,]*\]\{([\w|\s|\.|\~]+)\}")
    for line in f.readlines():
        presult = p.match(line)
        if presult :
            classoption = presult.group(1)
            classname   = presult.group(2)
        #
        if classname is None :
            qresult = None
        elif classname == "mn2e" :
            qresult = q_mn.match(line)
        elif classname == "elsarticle" :
            qresult = q_els.match(line)
        else :
            qresult = q.match(line)
        #
        if qresult : 
            firstauthor = qresult.group(1)
            break
    f.close()
    if classname :
        print("documentclass is %s"% classname)
    else :
        raise KindleException("missing classname?")
    if firstauthor :
        firstauthor = firstauthor.replace("~", " ")
        firstauthor = firstauthor.replace(". ", "_")
        try :
            if classname == "mn2e" :
                author = firstauthor.split()[0]
            else :
                author = firstauthor.split()[-1]
        except IndexError:
            author = "unknown"
    else :
        author = "unknown"
    print("author: %s"%author)
    return(classoption, classname, author)

def getClass(classname, clsfiles, bstfiles, desdir):
    if classname == "article" or classname == "old" :
        # safe
        return(None)
    clsfile = ".".join([classname, "cls"])
    if not (clsfile in clsfiles) :
        print("%s needed"%clsfile)
        if file_exists(os.path.join(clibDir, clsfile)):
            shutil.copy(os.path.join(clibDir, clsfile), desdir)
        else :
            raise KindleException("failed to find it in the cls library")
    bstfile = ".".join([classname, "bst"])
    if classname == "emulateapj" :
        # just copy the apj.bst file
        shutil.copy(os.path.join(clibDir, "apj.bst"), desdir)
    else :
        if not (bstfile in bstfiles) :
            if file_exists(os.path.join(clibDir, bstfile)):
                shutil.copy(os.path.join(clibDir, bstfile), desdir)
            else :
                print("probably the references will be messed up")

def getOpt(classoption):
    if classoption != "old" and classoption is not None :
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
    return(hasoptbracket, classopts)

def unTarAndModify(filename, year):
    try :
        print('%20s  is a tar file? %s \n continue' % (filename, tarfile.is_tarfile(filename)))
    except IOError, err :
        print('%20s  is a tar file? %s \n exiting' % (filename, err))
        return(None)
    # desdir: intermediate directory to store files and recompile, should be
    # non-existent otherwise will be wiped out the code
    desdir = os.path.join(saveDir, "outdir")
    force_mkdir(desdir)
    # open the tar file
    t = tarfile.open(filename, 'r')
    pdffiles = findFigs(t, "pdf")
    pngfiles = findFigs(t, "png")
    if len(pdffiles) > 0 or len(pngfiles) > 0:
        use_pdflatex = True
    else :
        use_pdflatex = False
    t.extractall(desdir)
    texfiles, clsfiles, bstfiles, bblfiles = examine_texenv(desdir)
    # go through all files
    masterfile, texversion = getMaster(texfiles, desdir)
    # deal with old latex2.09 files
    handleOldTeX(texversion, desdir)
    getBiblio(bblfiles, desdir)
    classoption, classname, author = checkMaster(masterfile, texversion)
    getClass(classname, clsfiles, bstfiles, desdir)
    hasoptbracket, classopts = getOpt(classoption)
    # parse class
    col_set, onecol_arg, twocol_arg = parse_documentclass(classname, classopts)
    # substitute
    kindlizeit(masterfile, hasoptbracket, classname, col_set, onecol_arg, twocol_arg)
    # recompile
    pdfout = do_latex(desdir, masterfile, use_pdflatex=use_pdflatex)
    # rename
    newpdfname = author + year + ".pdf"
    newpdf = os.path.join(desdir, newpdfname)
    shutil.move(pdfout, newpdf)
    return(newpdf)

def handleOldTeX(texversion, desdir) :
    if texversion == "latex2.09" :
        for file in old_files :
            fold = os.path.join(clibDir, file)
            shutil.copy(fold, desdir)

def batch_ps2eps(desdir, psfiles) :
    """ convert ps into eps"""
    if len(psfiles) == 0 :
        return([])
    epsfiles = []
    for psfile in psfiles :
        epsfile = psfile.replace(".ps", ".eps")
        cmd = " ".join(["ps2eps", os.path.join(desdir, psfile), os.path.join(desdir, epsfile)])
        print(cmd)
        os.system(cmd)
        fixeps = " ".join([os.path.join(origDir, "fixbbox.sh"), os.path.join(desdir, epsfile)])
        os.system(fixeps)
        epsfiles.append(epsfile)
    return(epsfiles)

   
def dropit(inpdf) :
    pdf = os.path.basename(inpdf)
    print("drop %s into dropbox %s"%(pdf, dropDir))
    despdf = os.path.join(dropDir, pdf)
    if file_exists(despdf):
        base = despdf.rstrip(".pdf")
        fsimi = glob(base+"*"+".pdf")
        for i in xrange(10):
            newpdf = base + "-" + str(i) + ".pdf"
            if newpdf in fsimi :
                continue
            else :
                shutil.copy(inpdf, newpdf)
                break
    else :
        shutil.copy(inpdf, despdf)

def do_latex(desdir, masterfile, use_pdflatex=False) :
    if use_pdflatex :
        mkfile = os.path.join(origDir, "Makefile_pdflatex")
    else :
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
        subst = kindlestr_apj+fontstr+r"\\begin{document}"+magnifystr
    elif classname == "mn2e" :
        subst = kindlestr_mn+fontstr+r"\\begin{document}"+magnifystr
    elif classname == "elsarticle" :
        subst = kindlestr_els+fontstr+r"\\begin{document}"+magnifystr
    elif classname == "old" :
        subst = r"\\begin{document}"+magnifystr
    else :
        subst = kindlestr+fontstr+r"\\begin{document}"+magnifystr
    substituteAll(masterfile, p, subst)
    # scale figures \includegraphics[width=xx]
    p = re.compile(r"\\includegraphics\[width=[\d|\.|\w|\s]+\]")
    subst = r"\includegraphics[width=1.0\\textwidth]"
    substituteAll(masterfile, p, subst)
    # switch names for bbl files \bibliography{ref_hshwang}
    p = re.compile(r"\\bibliography{\S+}")
    subst = r"\\bibliography{main}"
    substituteAll(masterfile, p, subst)
    # comment out banned package
    for pack in banned_packages :
        p = re.compile("[^\%]usepackage(.*)\{" + pack +"\}")
        commentALL(masterfile, p)


def parse_documentclass(classname, classopts):
    if classname == "old" :
        return("default", None, None)
    col_set = "default"
    if (classname == "elsart_mm"  or classname == "aa" or
        classname == "emulateapj" or classname == "aastex" or 
        classname == "elsarticle" or 
        classname == "mn2e"       or classname == "article") :
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
    print(newpdf)
    if newpdf :
        try :
            os.system("evince "+newpdf)
        except :
            os.system("mupdf2 "+newpdf)
    else :
        raise RuntimeError("failed")
    dropit(newpdf)


    


