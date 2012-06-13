#!/usr/bin/python
import sys, os, json
from hashlib import sha1

DEFAULT_DEVICE_PATH = "/media/Kindle"
ALLOWED_EXTENSIONS = ["pdf", "mobi", "azw", "txt", "prc"]
KINDLE_INTERNAL_PATH = "/mnt/us/documents/"

print "[#] Starting..."

# If path is not specified, use default device path
if len(sys.argv) < 2:
  print "[#] No device path specified, using default one"
  device_path = DEFAULT_DEVICE_PATH
# Else use path from the command line
else:
  device_path = sys.argv[1]

print "[#] Device path: %s" % device_path

COLLECTIONS_FILE_PATH = device_path + "/system/collections.json"
DOCUMENTS_DIR_PATH = device_path + "/documents/"


isnode = {}

# Function parses given folder, by creating new collection for it, adding all
# the files from this folder to the collection, and parsing all the subfolders
# recursively 
def ParseFolder(path, collections):
  # Path relative to DOCUMENTS_DIR_PATH
  relative_path = path.replace(DOCUMENTS_DIR_PATH, "")

  print "[#] Processing directory: ../%s" % relative_path[:-1]

  # Create new collection for current folder
  new_collection = {"items":[]}

  # Collection name is of the form directory - sub-directory - sub-sub-directory...
  collection_name = relative_path.replace("/", " - ")[:-1]

  isnode[collection_name] = False

  # Go through all the items in this directory
  for filename in os.listdir(path):
    # Check if is a file
    if os.path.isfile(path + filename):
      isnode[collection_name] = True
      # Get extension of that file
      extension = filename.split(".")[-1]
      # Check if file is the one we would want to add
      if extension in ALLOWED_EXTENSIONS:
        # Calculate SHA1 hash for the /mnt/us/<filename>
        the_sha = sha1((path + filename).replace(DOCUMENTS_DIR_PATH, 
                                                 KINDLE_INTERNAL_PATH))
        # Add this hash to a collection
        new_collection["items"].append("*%s" % the_sha.hexdigest())
    # Check if is directory
    elif os.path.isdir(path + filename):
      # Parse this sub-directory recursively
      ParseFolder(path + filename + "/", collections)


  # We do not want to add root directory to the collections
  if collection_name != '' and isnode[collection_name] is True:
    print("add {%s}"%collection_name)
    collections[collection_name + "@en-US"] = new_collection
   

try:
  # Check that such device path exists
  if not os.path.isdir(device_path):
    raise OSError(2, "Wrong device path")

  # Create dictionary for the collections
  collections = {}

  # Start from parsing the root direcory
  ParseFolder(DOCUMENTS_DIR_PATH, collections)

  # Convert collections to JSON
  collections_json = json.dumps(collections)

  print "[#] Collections list created"
  print "[#] Writing collections.json file..."

  # Write JSON to a collections.json
  f = open(COLLECTIONS_FILE_PATH, "w")
  f.write(collections_json)

  print "[#] Finished"

except Exception as e:
  print e
