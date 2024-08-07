__copyright__ = "Copyright 2021, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

import configparser
import subprocess
import time

from pathlib import Path
from typing import Union

from qgis.utils import pluginMetadata


def plugin_path(*args) -> Path:
    """Return the path to the plugin root folder."""
    path = Path(__file__).resolve().parent
    for item in args:
        path = path.joinpath(item)

    return path


def plugin_test_data_path(*args) -> Path:
    """Return the path to the plugin test data folder."""
    return plugin_path("tests", "fixtures", *args)


def timing(f):
    """
    Fonction qui permet de calculer le temps passé par une méthode
    Pour l'activer, ajouter simplement le décorateur @timing sur la méthode.
    """
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        print(f'{f.__name__:s} function took {(time2 - time1) * 1000.0:.3f} ms')

        return ret

    return wrap


def current_git_hash() -> str:
    """ Retrieve the current git hash number of the git repo (first 6 digit). """
    repo_dir = Path(__file__).parent
    git_show = subprocess.Popen(
        'git rev-parse --short=6 HEAD',
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        cwd=repo_dir,
        universal_newlines=True,
        encoding='utf8'
    )
    hash_number = git_show.communicate()[0].partition('\n')[0]
    if hash_number == '':
        hash_number = 'unknown'
    return hash_number


def next_git_tag():
    """ Using Git command, trying to guess the next tag. """
    repo_dir = Path(__file__).parent
    git_show = subprocess.Popen(
        'git describe --tags $(git rev-list --tags --max-count=1)',
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        cwd=repo_dir,
        universal_newlines=True,
        encoding='utf8'
    )
    try:
        tag = git_show.communicate()[0].partition('\n')[0]
    except IndexError:
        # Issue #374
        return "[no git tag]"

    if not tag:
        return 'next'

    versions = tag.split('.')
    text = f'{versions[0]}.{versions[1]}.{int(versions[2]) + 1}-pre'
    return text


def set_window_title() -> str:
    """ Set the window title if on a dev version. """
    version = pluginMetadata('cadastre', 'version')
    if version != 'master':
        return ''

    # return 'branch {}, commit {}, next {}'.format(
    #     version, current_git_hash(), next_git_tag())

    return f'next {next_git_tag()}'


def to_bool(val: Union[str, int, float, bool, None], default_value: bool = True) -> bool:
    """ Convert lizmap config value to boolean """
    if isinstance(val, bool):
        return val

    if val is None or val == '':
        return default_value

    if isinstance(val, str):
        # For string, compare lower value to True string
        return val.lower() in ('yes', 'true', 't', '1')

    elif not val:
        # For value like False, 0, 0.0, None, empty list or dict returns False
        return False

    return default_value


def metadata_config() -> configparser:
    """Get the INI config parser for the metadata file.

    :return: The config parser object.
    :rtype: ConfigParser
    """
    path = plugin_path("metadata.txt")
    config = configparser.ConfigParser()
    config.read(path, encoding='utf8')
    return config


def version(remove_v_prefix=True) -> str:
    """Return the version defined in metadata.txt."""
    v = metadata_config()["general"]["version"]
    if v.startswith("v") and remove_v_prefix:
        v = v[1:]
    return v
