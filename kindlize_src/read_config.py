import os
from ConfigParser import RawConfigParser


""" Read basic configurations from ~/.kindle.cfg file.
"""


class Config(object):
    def __init__(self, items):
        self._items = items
    @classmethod
    def from_raw_config(cls, config):
        return cls({
            'device'      : config.get('general', 'device'),
            'tmpDir'      : config.get('directory', 'tmpDir'),
            'dropDir'     : config.get('directory', 'dropDir'),
            'mountDir'    : config.get('directory', 'mountDir'),
            'incomingDir' : config.get('directory', 'incomingDir'),
            'font'        : config.get('LaTeX', 'font'),
            'fontheight'  : config.get('LaTeX', 'fontheight'),
            'fontwidth'   : config.get('LaTeX', 'fontwidth'),
            'pdfviewer'   : config.get('pdf',   'pdfviewer'),
        })

    def __getattr__(self, key):
        return self._items.get(key)

    def __getitem__(self, key):
        return self._items.get(key)

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self._items)

def load_config():
    config = RawConfigParser()
    config.read(os.path.expanduser('~/.kindle.cfg'))
    return(Config.from_raw_config(config))
