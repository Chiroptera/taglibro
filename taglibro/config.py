import json
import os.path


def generate_basic_config():
    conf = {}
    conf["journal_paths"] = []
    conf["exclude_strings"] = []

    return conf


def default_path():
    home = os.path.expanduser("~")
    path = os.path.join(home, '.taglibro.json')
    return path


def get_config():
    path = default_path()

    if not os.path.exists(path):
        config = generate_basic_config()
        with open(path, 'w') as f:
            config = json.dump(config, f)
    else:
        with open(path, 'r') as f:
            config = json.load(f)
        validate_config(config)
    return config


def store_config(config):
    path = default_path()

    validate_config(config)
    with open(path, 'w') as f:
        config = json.dump(config, f)


def validate_config(conf):
    if 'journal_paths' not in conf:
        raise TypeError('journal_paths not in config')
    if not isinstance(conf['journal_paths'], list):
        raise TypeError('journal_paths is not list')

    if 'exclude_strings' not in conf:
        raise TypeError('exclude_strings not in config')
    if not isinstance(conf['exclude_strings'], list):
        raise TypeError('exclude_strings is not list')


def add_folder(path):
    p = os.path.expandvars(path)
    p = os.path.expanduser(p)
    p = os.path.abspath(p)
    if not os.path.exists(p):
        raise Exception('path does not exist:', p)

    config = get_config()

    if p not in config['journal_paths']:
        config['journal_paths'].append(path)
    store_config(config)


def add_exclude_str(s):
    config = get_config()
    config['exclude_strings'].append(s)
    store_config(config)
