#!/usr/bin/env python
# Last-modified: 14 Jan 2013 02:11:54 AM

import os.path
from convert_arxiv import getTar, convert
from read_config import load_config

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
          metavar='arxiv_id', help="arXiv identifier, such as 1008.0641.")
        parser.add_argument('where',
          metavar='subdir', default="", help=" ".join(["which subdir under", dropDir, "to drop the final pdf."]))
        arxivid = parser.parse_args().id
        where   = parser.parse_args().where
    else :
        parser = OptionParser(usage="usage: %kindlize.py arxiv_id subdir \n  where subdir is a subdirectory under " + dropDir)
        options, args = parser.parse_args()
        if len(args) != 2 :
            raise RuntimeError("missing arguments.")
        arxivid = args[0]
        where   = args[1]
    return(arxivid, where)



def main():
    config = load_config()
    arxivid, where = parse_args(config.dropDir)
    # directories
    saveDir = os.path.expanduser(config.tmpDir)
    origDir = os.path.expanduser(config.installDir)
    clibDir = os.path.expanduser(os.path.join(origDir, "clslib"))
    dropDir = os.path.expanduser(config.dropDir)

    fname, year = getTar(arxivid, saveDir)
    newpdf = convert(fname, year, saveDir, origDir, clibDir, dropDir, config.font, config.fontheight, config.fontwidth)
    print newpdf



    # Config({'incomingDir': '/media/Kindle/documents/Incoming/', 'dropDir': '~/Dropbox/kindle_sync/', 'fontheight': '14pt', 'device': 'Kindle DX', 'fontwidth': '18pt', 'font': 'charter', 'installDir': '~/mercurial/kindlize/', 'tmpDir': '~/tmp/'})

if __name__ == '__main__' :
    main()
