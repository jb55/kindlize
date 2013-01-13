import os
from ConfigParser import RawConfigParser



class Config(object):
    def __init__(self, items):
        self._items = items
    @classmethod
    def from_raw_config(cls, config):
        return cls({
            'kindleaddress' : config.get('general', 'kindleaddress'),
            'logpath'       : config.get('general', 'logpath'),
            'username'      : config.get('email', 'username'),
            'server'        : config.get('email', 'server'),
            'port'          : config.getint('email', 'port'),
            'mode'          : config.get('email', 'mode'),
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
    return Config.from_raw_config(config)

def main():
    config = load_config()

    print config.username

if __name__ == '__main__':
    main()

