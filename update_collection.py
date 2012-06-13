#Last-modified: 13 Jun 2012 02:16:30 AM
import json
import os.path
import hashlib


HASH_PREFIX = "/mnt/us/documents/"

class Collection(object):
    def __init__(self, root="/media/Kindle/"):
        self.root = root
        self.load()

    def load(self):
        fcln = os.path.join(self.root, "system", "collections.json")
        f    = file(fcln, "r")
        self.cln = json.load(f)
        self.cnames = self.cln.keys()

    def update(self, c, fname):
        new_hal = gethash(fname)
        _c = " ".join([c, "-@en-US"]) 
        if _c in self.cnames :
            print("collection %s exists, append..."%_c)
            self.cln[_c]["items"].append("*%s" % new_hal)
        else :
            print("collection %s does not exist, create..."%_c)
            new_collection = {"items":[]}
            new_collection["items"].append("*%s" % new_hal)
            self.cln[_c] = new_collection



def gethash(fname):
    hin = os.path.join(HASH_PREFIX, fname)
    hobj = hashlib.sha1(hin)
    hval = hobj.hexdigest()
    return(hval)




if __name__ == "__main__":    
    cln = Collection()
    cln.update("Incoming - arxiv", "shit")
