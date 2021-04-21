__copyright__ = "Copyright 2021, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

import unittest

from pathlib import Path

from cadastre.edigeo_parser import Commune, Parser
from cadastre.processing.algorithms.edigeo_downloader import EdigeoDownloader


class TestEdigeoParser(unittest.TestCase):

    def setUp(self) -> None:
        self.url = EdigeoDownloader.url()

    def test_commune(self):
        """ Test the URL for a given commune. """
        commune = Commune('05017', base_url=self.url)
        self.assertEqual('05', commune.departement)
        self.assertEqual(
            commune.url,
            'https://cadastre.data.gouv.fr/data/dgfip-pci-vecteur/latest/edigeo/feuilles/05/05017/'
        )
        self.assertListEqual([], commune.feuilles)
        self.assertEqual('05', commune.departement)
        self.assertEqual('05017', commune.insee)
        self.assertEqual('latest', commune.date)

        commune = Commune('05017', date='2021-02-01', base_url=self.url)
        self.assertEqual(
            commune.url,
            'https://cadastre.data.gouv.fr/data/dgfip-pci-vecteur/2021-02-01/edigeo/feuilles/05/05017/'
        )
        self.assertListEqual([], commune.feuilles)

        # Outre-mer
        commune = Commune('97124')
        self.assertEqual('971', commune.departement)
        self.assertEqual('', commune.url)

    def test_parse_index_page(self):
        """ Test we can parse the index page from Edigeo. """
        commune = Commune('05017', base_url=self.url)
        folder = Path(__file__).parent
        fixture = Path("fixtures/listing_edigeo_feuilles.html")
        parser = Parser(folder.joinpath(fixture), commune)

        self.assertListEqual([], parser.feuilles)
        self.assertIsNone(parser.count)

        parser.parse()

        self.assertEqual(15, parser.count)
        self.assertEqual(15, len(commune.feuilles))
        self.assertEqual(1763, commune.total_size)

        feuille = commune.feuilles[0]

        self.assertEqual('050170000A01', feuille.name)
        self.assertEqual(
            'https://cadastre.data.gouv.fr/data/dgfip-pci-vecteur/latest/edigeo/feuilles/05/05017/'
            'edigeo-050170000A01.tar.bz2',
            commune.url_feuille(feuille))
