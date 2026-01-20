from pathlib import Path

import pytest

from cadastre.edigeo_parser import Commune, Parser
from cadastre.processing.algorithms.edigeo_downloader import EdigeoDownloader


@pytest.fixture(scope="module") 
def url() -> str:
    return EdigeoDownloader.url()


def test_commune(url: str):
    """ Test the URL for a given commune. """
    commune = Commune('05017', base_url=url)
    assert commune.departement == "05"
    assert commune.url == 'https://cadastre.data.gouv.fr/data/dgfip-pci-vecteur/latest/edigeo/feuilles/05/05017/'
    assert commune.feuilles == []
    assert commune.departement == "05"
    assert commune.insee == "05017"
    assert commune.date == "latest"

    commune = Commune('05017', date='2021-02-01', base_url=url)
    assert commune.url == 'https://cadastre.data.gouv.fr/data/dgfip-pci-vecteur/2021-02-01/edigeo/feuilles/05/05017/'
    
    assert commune.feuilles == []

    # Outre-mer
    commune = Commune('97124')
    assert commune.departement == "971"
    assert commune.url == ""


def test_parse_index_page(url: str, fixtures: Path):
    """ Test we can parse the index page from Edigeo. """
    commune = Commune('05017', base_url=url)
    fixture = fixtures.joinpath("listing_edigeo_feuilles.html")
    parser = Parser(fixture, commune)

    assert parser.feuilles == []
    assert parser.count is None

    parser.parse()

    assert parser.count == 15
    assert len(commune.feuilles) == 15
    assert commune.total_size == 1763

    feuille = commune.feuilles[0]

    assert feuille.name == "050170000A01"
    assert commune.url_feuille(feuille) == (
        'https://cadastre.data.gouv.fr/data/dgfip-pci-vecteur/'
        'latest/edigeo/feuilles/05/05017/'
        'edigeo-050170000A01.tar.bz2'
    )


def test_filter(url: str, fixtures: Path):
    """ Test the filter. """
    fixture = fixtures.joinpath("listing_edigeo_feuilles.html")

    # Single generic
    commune = Commune('05017', base_url=url)
    parser = Parser(fixture, commune, ['0C'])
    parser.parse()
    expected = ['050170000C01', '050170000C02', '050170000C03']
    assert [f.name for f in parser.feuilles] == expected

    # Two generic
    commune = Commune('05017', base_url=url)
    parser = Parser(fixture, commune, ['0C', 'AA'])
    parser.parse()
    expected = ['050170000C01', '050170000C02', '050170000C03', '05017000AA01']
    assert [f.name for f in parser.feuilles] == expected

    # One precise
    commune = Commune('05017', base_url=url)
    parser = Parser(fixture, commune, ['050170000C03'])
    parser.parse()
    expected = ['050170000C03']
    assert [f.name for f in parser.feuilles] == expected

    # Two precise
    commune = Commune('05017', base_url=url)
    parser = Parser(fixture, commune, ['050170000C03', '050170000D01'])
    parser.parse()
    expected = ['050170000C03', '050170000D01']
    assert [f.name for f in parser.feuilles] == expected

    # One generic and one precise
    commune = Commune('05017', base_url=url)
    parser = Parser(fixture, commune, ['0C', '050170000D01'])
    parser.parse()
    expected = ['050170000C01', '050170000C02', '050170000C03', '050170000D01']
    assert [f.name for f in parser.feuilles] == expected

    # Subset
    commune = Commune('05017', base_url=url)
    parser = Parser(fixture, commune, ['0D', '050170000D01'])
    parser.parse()
    expected = ['050170000D01']
    assert [f.name for f in parser.feuilles] == expected

    # None
    commune = Commune('05017', base_url=url)
    parser = Parser(fixture, commune, ['ZZ'])
    parser.parse()
    expected = []
    assert [f.name for f in parser.feuilles] == expected
