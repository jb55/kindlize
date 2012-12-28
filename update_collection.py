#!/usr/bin/env python
#Last-modified: 27 Dec 2012 11:52:57 PM
import json
import os.path
import hashlib


HASH_PREFIX = "/mnt/us/documents/"
ALLOWED_EXTENSIONS = ["pdf", "mobi", "azw", "txt", "prc"]

class Collection(object):
    def __init__(self, root="/media/Kindle/"):
        """ Initialize the Collection class, load the existing class.
        """
        self.root = root
        # load the current collections
        self.load()

    def load(self):
        """ load existing collection json file.
        """
        fcln = os.path.join(self.root, "system", "collections.json")
        f    = file(fcln, "r")
        # json file
        self.cln = json.load(f)
        # all the collection names
        self.cnames = self.cln.keys()
        f.close()

    def update(self, c, new_hal, fname):
        """ update collection and new_hal to the database.
        """
        _c = " ".join([c, "-@en-US"]) 
        if _c in self.cnames :
            if new_hal in self.cln[_c]["items"] or "*"+new_hal in self.cln[_c]["items"] :
                pass
            else :
                print("file %s does not exist in %s..."%(fname, _c))
                print("append file %s to %s..."%(fname, _c))
                self.cln[_c]["items"].append("*%s" % new_hal)
        else :
            print("collection %s does not exist, create..."%_c)
            print("append file %s to %s..."%(fname, _c))
            new_collection = {"items":[]}
            new_collection["items"].append("*%s" % new_hal)
            self.cln[_c] = new_collection
            self.cnames  = self.cln.keys()

    def forage(self, folder="incoming"):
        """ detect new files and merge them into data base.
        """
        if folder.startswith("/") :
            raise RuntimeError("folder needs to be a dir relative to <documents>")
        elif len(folder) == 0 :
            isnode = True
            path = os.path.join(self.root, "documents")
        else :
            isnode = False
            path = os.path.join(self.root, "documents", folder)
        if not os.path.isdir(path) :
            print("folder %s does not exist, exit..." % folder)
        else  :
            print("foraging directory : %s" % folder)
        if isnode :
            current_collection = None
            print("at root node")
        else :
            current_collection = folder.replace("/", " - ")
            print("Current collection name : %s" % current_collection)
        # Go through all the files in this directory
        for filename in os.listdir(path):
            # Check if is a file
            if os.path.isfile(os.path.join(path, filename)) and (not isnode):
                # Get extension of that file
                extension = filename.split(".")[-1]
                # Check if file is the one we would want to add
                if extension in ALLOWED_EXTENSIONS :
                    # Calculate SHA1 hash for the /mnt/us/<folder>/<filename>
                    old_hal = gethash(os.path.join(folder, filename))
                    self.update(current_collection, old_hal, filename)
            # Check if is directory
            elif os.path.isdir(os.path.join(path, filename)):
                    # Parse this sub-directory recursively
                    self.forage(folder=os.path.join(folder, filename))

    def save(self, outdir=None) :
        """ Convert collections to JSON
        """
        collections_json = json.dumps(self.cln)
        # Write JSON to a collections.json
        if outdir is None :
            json_path = os.path.join(self.root, "system", "collections.json")
        else :
            json_path = outdir
        print("Writing collections.json file to %s" % json_path)
        f = open(json_path, "w")
        f.write(collections_json)
        f.close()

    def default(self) :
        self.cln    = {}
        self.cnames = []
        self.forage(folder="")

def gethash(fname):
    """ get hash string.
    """
    hin = os.path.join(HASH_PREFIX, fname)
    hobj = hashlib.sha1(hin)
    hval = hobj.hexdigest()
    return(hval)

if __name__ == "__main__":    
    cln = Collection()
    cln.forage(folder="Incoming/arxiv")
#    cln.default()
    cln.save()
