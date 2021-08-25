import re

from pathlib import Path
from typing import NamedTuple, Union

__copyright__ = "Copyright 2021, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"


class Feuille(NamedTuple):
    link: str = None
    name: str = None
    day: str = None
    month: str = None
    year: str = None
    size: str = None

    def __str__(self):
        return self.name


class Commune:

    def __init__(self, insee: str, date: str = "latest", feuilles=None, base_url=None):
        self.insee = insee
        self.date = date
        self.feuilles = feuilles
        if self.feuilles is None:
            self.feuilles = []

        self.base_url = base_url

    @property
    def departement(self) -> str:
        if self.insee.startswith('97'):
            return self.insee[0:3]
        else:
            return self.insee[0:2]

    @property
    def url(self):
        if self.base_url is None:
            return ''

        return self.base_url.format(
            date=self.date,
            departement=self.departement,
            commune=self.insee,
        )

    def url_feuille(self, feuille: Feuille) -> str:
        return self.url + feuille.link

    @property
    def total_size(self) -> int:
        size = 0
        for feuille in self.feuilles:
            size += int(feuille.size)
        return size

    def __str__(self):
        return '{} ({})'.format(self.insee, self.departement)


class Parser:

    @classmethod
    def regex(cls):
        # TODO : Provide a simple regex looking for "(.*).tar.bz2"
        return r'<a href="(.*)">edigeo-([a-zA-Z0-9\-]+)\.tar\.bz2<\/a>\s+(\d{2})-(\w+)-(\d{4})\s.*\s\s(\d*)K'

    def __init__(
            self, file_path: Union[Path, str], commune: Commune, feuille_filter: Union[str, list, None] = None):
        self._count = None

        self.feuille_filter = None
        if isinstance(feuille_filter, str):
            self.feuille_filter = feuille_filter.split(',')
        elif isinstance(feuille_filter, list):
            self.feuille_filter = feuille_filter

        if isinstance(file_path, str):
            file_path = Path(file_path)

        self.file_path = file_path
        self.commune = commune

    @property
    def count(self) -> Union[int, None]:
        return self._count

    @property
    def feuilles(self) -> list:
        return self.commune.feuilles

    def parse(self):
        with self.file_path.open(mode="r", encoding='utf8') as f:
            content = f.readlines()

        for line in content:
            results = re.findall(
                pattern=self.regex(), string=line, flags=re.DOTALL
            )

            if not len(results):
                continue

            if self.feuille_filter:
                for one_filter in self.feuille_filter:
                    if one_filter in results[0][1]:
                        self.commune.feuilles.append(Feuille(*results[0]))
                        break
            else:
                self.commune.feuilles.append(Feuille(*results[0]))

        self._count = len(self.feuilles)
