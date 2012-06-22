#!/bin/bash

rsync -av --delete --exclude "*.mbp" --exclude "*.pdr" ~/Dropbox/kindle_sync/ /media/Kindle/documents/Incoming/
