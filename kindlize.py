#!/usr/bin/env python
# Last-modified: 15 Jan 2013 12:14:10 AM

import os.path
import pkgutil
import re
from subprocess import Popen, PIPE
from kindlize_src.convert_arxiv import getTar, convert, correct_unknown_author, dropit
from kindlize_src.read_config import load_config
from kindlize_src.update_collection import Collection

def parse_args(dropDir):
    """ Parsing command-line arguments, compatible with both
    python2.6 (optparse) and 2.7 (argparse).
    """
    try :
        import argparse
        hasargparse = True
    except ImportError :
        from optparse import OptionParser
        hasargparse = False
    # environment dependent parsing.
    if hasargparse :
        parser = argparse.ArgumentParser(
          description="""Kindlize pdfs from arXiv""")
        parser.add_argument('id',
          metavar='arxiv_id', nargs='?', default="0", help="arXiv identifier, such as 1008.0641.")
        parser.add_argument('where',
          metavar='subdir', nargs='?', default=".", help=" ".join(["which subdir under", dropDir, "to drop the final pdf."]))
        arxivid = parser.parse_args().id
        where   = parser.parse_args().where
    else :
        parser = OptionParser(usage="usage: %kindlize.py arxiv_id subdir \n  where subdir is a subdirectory under " + dropDir)
        options, args = parser.parse_args()
        if len(args) == 0 :
            arxivid = "0"
            where   = "."
        elif len(args) == 1 :
            raise RuntimeError("missing arguments.")
        elif len(args) == 2 :
            arxivid = args[0]
            where   = args[1]
    return(arxivid, where)

def preview_pdf(newpdf, pdfviewer):
    if newpdf :
        print(Popen(" ".join([pdfviewer, newpdf]), stdout=PIPE, shell=True).stdout.read())
    else :
        raise RuntimeError("kindlize failed to generate the pdf.")

def detect_kindle(incomingDir):
    if os.path.isdir(incomingDir) :
        print("%s exists, Kindle seems to be connected." % incomingDir)
        return(True)
    else :
        print("%s does not exist, Kindle seems to be disconnected." % incomingDir)
        print("usage: kindlize [-h] [arxiv_id] [subdir]")
        return(False)

def sync_kindle_folder(dropDir, incomingDir) :
    """
    """
    print("syncing %s to %s" % (incomingDir, dropDir))
    print(Popen(" ".join(["rsync", "-av", "--delete", "--exclude", "*.mbp", "--exclude", "*.pdr", dropDir, incomingDir]), stdout=PIPE, shell=True).stdout.read())


def _main():
    config  = load_config()
    origDir = os.path.dirname(os.path.realpath(__file__))
    # expand HOME variable to get full directories.
    saveDir     = os.path.expanduser(config.tmpDir)
    clibDir     = os.path.expanduser(os.path.join(origDir, 
        "kindlize_src", "clslib"))
    dropDir     = os.path.expanduser(config.dropDir)
    incomingDir = os.path.expanduser(config.incomingDir)
    # get the relative path of incomingDir under document/
    result = re.search('Kindle/documents/(.*)', incomingDir)
    subDir = result.group(1)
    # print("Please make sure subdir %s exists in your Kindle" % subDir)
    # read commandline arguments.
    arxivid, where = parse_args(config.dropDir)
    # do pdf conversion when arxvid is nonzero.
    if arxivid != "0" :
        # download and save the tar file to saveDir, alse derive the year of publication.
        fname, year = getTar(arxivid, saveDir)
        # unpack and produce the kindle-friendly pdf file.
        _newpdf = convert(fname, year, saveDir, clibDir, dropDir, config.font, config.fontheight, config.fontwidth)
        newpdf  = correct_unknown_author(_newpdf)
        # preview the file
        preview_pdf(newpdf, config.pdfviewer)
        # drop it to dropDir
        dropit(newpdf, dropDir, where)
    # simply update incoming directory if no commandline arguments available.
    else :
        if detect_kindle(incomingDir) :
            sync_kindle_folder(dropDir, incomingDir)
            cln = Collection()
            if where == "." :
                # prevent funky "/./" in folder
                folder = subDir
            else :
                folder = os.path.join(subDir, where)
            cln.forage(folder=folder)
            cln.save()
            print("Kindle Collection is updated (required reboot of your Kindle devide).")


    



if __name__ == '__main__' :
    _main()
