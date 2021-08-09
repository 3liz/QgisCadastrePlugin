__copyright__ = "Copyright 2021, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

import time


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
