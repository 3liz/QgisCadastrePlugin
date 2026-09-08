import re

from datetime import datetime
from pathlib import Path
from typing import (
    Iterator,
    NamedTuple, 
    Union,
)

__copyright__ = "Copyright 2021, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"


class Feuille(NamedTuple):
    link: str
    name: str
    size: int       # XXX: Not used in plugin
    date: datetime  # XXX: Not used in plugin

    def __str__(self):
        return self.name


class Commune:

    def __init__(
        self,
        insee: str, 
        date: str = "latest", 
        feuilles: list[Feuille] | None = None, 
        base_url: str | None = None,
    ):
        self.insee = insee
        self.date = date
        self.feuilles = feuilles if feuilles is not None else []
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
            size += feuille.size
        return size

    def __str__(self):
        return f'{self.insee} ({self.departement})'


class Parser:

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

        content = self.file_path.read_text()

        for (link, name, size, date) in _html_parse(content):

            if self.feuille_filter:
                for one_filter in self.feuille_filter:
                    if one_filter in name:  # ???!!! 
                        self.commune.feuilles.append(Feuille(link, name, size, date))
                        break
            else:
                self.commune.feuilles.append(Feuille(link, name, size, date))

        self._count = len(self.feuilles)



CODE_RE = re.compile("edigeo(?:-cc)?-([a-zA-Z0-9\-]+)\.tar\.bz2")

def _html_parse(index: str) -> Iterator[tuple[str, str, int, datetime]]:
    from .xmltodict import parse

    tag_start = "<tbody>"
    tag_end = "</tbody>"

    # Strip anything outside of <tbody></tbody>
    start, end = index.find(tag_start), index.rfind(tag_end) + len(tag_end)
    for td in parse(index[start:end])["tbody"]["tr"][1:]:
        td = td["td"]
        #link = td[0]["a"]["@href"] 
        name = td[0]["a"]["#text"]
        link = name
        size = int(td[1])
        date = datetime.fromisoformat(td[2])
        if m := CODE_RE.match(name):
            name = m.groups()[0]
            yield link, name, size, date

