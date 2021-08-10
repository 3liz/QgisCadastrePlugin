__copyright__ = "Copyright 2021, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

import subprocess
import time

from pathlib import Path

from qgis.utils import pluginMetadata


def timing(f):
    """
    Fonction qui permet de calculer le temps passé par une méthode
    Pour l'activer, ajouter simplement le décorateur @timing sur la méthode.
    """
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        print('{:s} function took {:.3f} ms'.format(f.__name__, (time2 - time1) * 1000.0))

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
    tag = git_show.communicate()[0].partition('\n')[0]
    if not tag:
        return 'next'
    versions = tag.split('.')
    text = '{}.{}.{}-pre'.format(versions[0], versions[1], int(versions[2]) + 1)
    return text


def set_window_title() -> str:
    """ Set the window title if on a dev version. """
    version = pluginMetadata('cadastre', 'version')
    if version != 'master':
        return ''

    # return 'branch {}, commit {}, next {}'.format(
    #     version, current_git_hash(), next_git_tag())

    return 'next {}'.format(next_git_tag())
