import json, os, sys

from base64 import b64decode

class Config:
    token = ''
    prefix = ''
    apikeys = {}


def make():
    with open('config.json', 'w+') as fd:
        fd.write(json.dumps({
            'token': 'your token here!',
            'prefix': '.',
            'apikeys': {}
        },
        indent=4
    ))

def save_config():
    with open('config.json', 'w+') as fd:
        fd.write(json.dumps({
            'token': Config.token,
            'prefix': Config.prefix,
            'apikeys': Config.apikeys
        },
        indent=4
    ))

def load_config():
    if not os.path.exists('config.json'):
        print('Config not found, creating!')
        make()

    with open(
        'config.json',
        buffering=2048*2048
    ) as fd:
        cfg = json.loads(fd.read())

    try:
        tk_format, tk_str = cfg['token'].split(':')

        if tk_format == 'base64' \
        or tk_format == 'b64':
            tk_str = b64decode(tk_str.encode()).decode()
    except Exception:
        tk_str = cfg['token']

    
    if tk_str == 'your token here!':
        sys.exit('\nIt seems like you\'ve forget to edit your token. \nPlease do that first before continuing!')
    
    try:
        Config.token = tk_str
        Config.prefix = cfg['prefix']

        Config.apikeys = cfg['apikeys']
    
    except Exception as e:
        sys.exit(f'\nError while reading from config file: {str(e).rstrip()}')
    
