#!/usr/bin/env python3
"""Generate a FICTITIOUS MAJIC data set for the commune 13029 CORNILLON-CONFOUX.

ALL THE GENERATED DATA IS FICTITIOUS: owners, names, birth dates and places, addresses, SIREN numbers,
buildings, evaluations and amounts are invented and do not describe any real person or property.

The parcels come from the EDIGEO test data (parcelles_edigeo_13029.csv, extracted from an import
of tests/fixtures/edigeo/13029), so that MAJIC and EDIGEO data are linked after the import.

The record layouts follow the MAJIC 2026 descriptions (docs/media/pdf/MAJIC/2026)
and the positions read by cadastre/scripts/plugin/2026/majic3_formatage_donnees.sql.

Usage: python3 generate_majic_13029.py
It writes the REV*.800 files and TOPO_test.csv into the 13029 directory, the output is always the same.
"""

import csv
import random

from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "13029"

DEP = "13"
DIR = "2"
COM = "029"
LIBCOM = "CORNILLON-CONFOUX"
LIBDIR = "BOUCHES-DU-RHONE-AIX"
ANNEE = "2026"
DATE_FICHIER = "04052026"
CCOCIF = "1309"
CCPPER = "009"
CODE_POSTAL = "13250"

rng = random.Random(13029)


# ---------------------------------------------------------------- records


class Record:
    """A fixed length record, positions start at 1 like in the MAJIC descriptions."""

    def __init__(self, length: int):
        self.chars = [" "] * length

    def text(self, start: int, length: int, value: str) -> "Record":
        value = str(value)[:length].ljust(length)
        self.chars[start - 1 : start - 1 + length] = list(value)
        return self

    def num(self, start: int, length: int, value: int) -> "Record":
        return self.text(start, length, str(int(value)).zfill(length))

    def __str__(self) -> str:
        return "".join(self.chars)


def headers(length: int, libdir_pos: int, parmdat_pos: int, libcom_pos: int = 17) -> list[str]:
    """Head of direction and commune records"""
    head = Record(length).text(1, 2, DEP).text(3, 1, DIR).text(libdir_pos, 30, LIBDIR)
    head.text(parmdat_pos, 2, "D4").text(parmdat_pos + 2, 8, DATE_FICHIER)
    commune = Record(length).text(1, 2, DEP).text(3, 1, DIR).text(4, 3, COM).text(libcom_pos, 30, LIBCOM)
    return [str(head), str(commune)]


# ---------------------------------------------------------------- reference data

# Voies of the TOPO file: code rivoli, nature, libelle
VOIES = [
    ("0150", "VC", "MONTEE DES AIRES"),
    ("0870", "CHE", "DE CAMPREOUX"),
    ("1400", "RTE", "DE CONFOUX"),
    ("1500", "CHEM", "DE LA COOPERATIVE"),
    ("2650", "RUE", "DU FIGUIER"),
    ("4925", "CHE", "DES LOUANES"),
    ("5450", "RUE", "DU MASE"),
    ("7550", "ALL", "DU ROMARIN"),
    ("A321", "CITE", "DES AIRES"),
]
# Lieux-dits of the TOPO file, the same as the EDIGEO lieux-dits
LIEUX_DITS = [
    ("B020", "BEAUME CORNILLONE"),
    ("B030", "BELVEZET"),
    ("B095", "GOUFRAN"),
    ("B060", "LES PLAINES DES ASTIERS"),
    ("B080", "PIELE"),
    ("B111", "LE LIS"),
]
# Lieux-dits added to the original TOPO test file
TOPO_NOUVEAUX_LIEUX_DITS = ["B020", "B030", "B060", "B080"]


def ccovoi(ccoriv: str) -> str:
    """Code MAJIC of the voie, 5 characters"""
    return ccoriv.rjust(5, "0")


NOMS = [
    "ARNAUD", "BARRE", "BERNARD", "BLANC", "BONNET", "BOYER", "BRUN", "CARRE", "CHABAUD", "CLEMENT",
    "COSTE", "DAUMAS", "DURAND", "ESTIENNE", "FABRE", "FAURE", "FERAUD", "GARCIN", "GAUTIER", "GIRAUD",
    "GUIEN", "HUGUES", "IMBERT", "JULLIEN", "LAUGIER", "LEGRAND", "MARTIN", "MASSE", "MAUREL", "MICHEL",
    "MOREL", "NICOLAS", "OLIVE", "PASCAL", "PAYAN", "PELLEGRIN", "PERRIN", "REYNAUD", "RICHARD", "ROUX",
    "ROUBAUD", "SICARD", "SIMON", "TOURNIER", "VIDAL", "VIAL", "VINCENT", "ZUNINO",
]
PRENOMS_H = [
    "ALAIN", "ANDRE", "BERNARD", "CHRISTIAN", "DANIEL", "DIDIER", "ERIC", "FRANCOIS", "GERARD", "GILLES",
    "JACQUES", "JEAN", "JEAN PIERRE", "LAURENT", "LOUIS", "MARC", "MICHEL", "NICOLAS", "PATRICK", "PAUL",
    "PHILIPPE", "PIERRE", "ROBERT", "SERGE", "THIERRY", "THOMAS", "YVES",
]
PRENOMS_F = [
    "ANNE", "BRIGITTE", "CATHERINE", "CHANTAL", "CHRISTINE", "CLAIRE", "DOMINIQUE", "FRANCOISE", "HELENE",
    "ISABELLE", "JACQUELINE", "JULIE", "MARIE", "MARTINE", "MONIQUE", "NATHALIE", "ODILE", "PATRICIA",
    "SANDRINE", "SOPHIE", "SYLVIE", "VALERIE", "VERONIQUE",
]
LIEUX_NAISSANCE = [
    "13 MARSEILLE", "13 AIX EN PROVENCE", "13 SALON DE PROVENCE", "13 ISTRES", "13 MIRAMAS",
    "13 LANCON PROVENCE", "13 ARLES", "84 AVIGNON", "84 CAVAILLON", "30 NIMES", "83 TOULON", "06 NICE",
    "69 LYON", "75 PARIS", "34 MONTPELLIER", "31 TOULOUSE", "33 BORDEAUX", "38 GRENOBLE",
]
# Addresses outside the commune: number, nature, libelle, code postal, commune
ADRESSES_EXTERIEURES = [
    ("0012", "BD", "MICHELET", "13008", "MARSEILLE"),
    ("0045", "AV", "DE LA REPUBLIQUE", "13300", "SALON DE PROVENCE"),
    ("0003", "RUE", "DES CORDELIERS", "13100", "AIX EN PROVENCE"),
    ("0127", "AV", "JEAN JAURES", "69007", "LYON"),
    ("0008", "RUE", "DE LA ROQUETTE", "75011", "PARIS"),
    ("0021", "CHE", "DES VIGNES", "13680", "LANCON PROVENCE"),
    ("0056", "RUE", "DES LICES", "84000", "AVIGNON"),
    ("0002", "IMP", "DES OLIVIERS", "13140", "MIRAMAS"),
]


# ---------------------------------------------------------------- owners


@dataclass
class Adresse:
    dnvoiri: str
    natvoi: str
    libvoi: str
    code_postal: str
    commune: str
    ccoriv: str = ""

    def dlign4(self) -> str:
        # number (4), repetition index (1), nature (4), libelle (27)
        return self.dnvoiri.rjust(4, "0") + " " + self.natvoi.ljust(4) + self.libvoi[:27]

    def dlign6(self) -> str:
        return f"{self.code_postal} {self.commune}"


@dataclass
class Personne:
    dnuper: str
    gtoper: str  # 1 physique, 2 morale
    ccodro: str
    adresse: Adresse
    ccodem: str = ""
    nom: str = ""
    prenom: str = ""
    ccoqua: str = ""  # 1 M, 2 MME
    naissance: str = ""  # JJ/MM/AAAA
    lieu_naissance: str = ""
    denomination: str = ""  # personne morale
    ccogrm: str = ""
    dnatpr: str = ""
    dforme: str = ""
    dformjur: str = ""
    dsiren: str = ""
    destinataire: bool = False


@dataclass
class Compte:
    dnupro: str
    personnes: list[Personne] = field(default_factory=list)


used_dnuper: set[str] = set()


def dnuper(prefix: str) -> str:
    while True:
        value = prefix + "".join(rng.choice("ABCDEFGHJKLMNPRSTVWXZ0123456789") for _ in range(5))
        if value not in used_dnuper:
            used_dnuper.add(value)
            return value


def adresse_commune() -> Adresse:
    ccoriv, natvoi, libvoi = rng.choice(VOIES)
    return Adresse(str(rng.randint(1, 120)), natvoi, libvoi, CODE_POSTAL, LIBCOM.replace("-", " "), ccoriv)


def adresse_exterieure() -> Adresse:
    numero, natvoi, libvoi, code_postal, commune = rng.choice(ADRESSES_EXTERIEURES)
    return Adresse(numero, natvoi, libvoi, code_postal, commune)


def personne_physique(ccodro: str, nom: str, femme: bool, adresse: Adresse, ccodem: str = "") -> Personne:
    annee = rng.randint(1938, 1998)
    return Personne(
        dnuper=dnuper("M"),
        gtoper="1",
        ccodro=ccodro,
        ccodem=ccodem,
        nom=nom,
        prenom=rng.choice(PRENOMS_F if femme else PRENOMS_H),
        ccoqua="2" if femme else "1",
        naissance=f"{rng.randint(1, 28):02d}/{rng.randint(1, 12):02d}/{annee}",
        lieu_naissance=rng.choice(LIEUX_NAISSANCE),
        adresse=adresse,
    )


class Comptes:
    def __init__(self):
        self.comptes: list[Compte] = []
        self.numbers: dict[str, int] = {}

    def new(self, group: str, personnes: list[Personne]) -> Compte:
        self.numbers[group] = self.numbers.get(group, 0) + 1
        compte = Compte(f"{group}{self.numbers[group]:05d}", personnes)
        if not any(p.destinataire for p in personnes):
            personnes[0].destinataire = True
        self.comptes.append(compte)
        return compte

    def physique(self) -> Compte:
        """A compte of physical persons, with different kinds of rights"""
        nom = rng.choice(NOMS)
        adresse = adresse_commune() if rng.random() < 0.7 else adresse_exterieure()
        kind = rng.choices(["seul", "couple", "indivision", "demembrement"], weights=[50, 30, 10, 10])[0]
        if kind == "seul":
            personnes = [personne_physique("P", nom, rng.random() < 0.5, adresse)]
        elif kind == "couple":
            personnes = [
                personne_physique("P", nom, False, adresse),
                personne_physique("P", nom, True, adresse),
            ]
        elif kind == "indivision":
            personnes = [
                personne_physique("P", nom, rng.random() < 0.5, adresse, "I")
                for _ in range(rng.randint(2, 3))
            ]
        else:
            # The widow is usufructuary, the children are bare owners
            personnes = [personne_physique("U", nom, True, adresse, "V")]
            personnes += [
                personne_physique("N", nom, rng.random() < 0.5, adresse_exterieure()) for _ in range(2)
            ]
        return self.new(nom[0], personnes)

    def morale(self, denomination: str, ccogrm: str, dforme: str, dformjur: str, **kwargs) -> Compte:
        adresse = kwargs.pop("adresse", None) or adresse_commune()
        personnes = [
            Personne(
                dnuper=dnuper("P"),
                gtoper="2",
                ccodro=kwargs.pop("ccodro", "P"),
                denomination=denomination,
                ccogrm=ccogrm,
                dforme=dforme,
                dformjur=dformjur,
                adresse=adresse,
                **kwargs,
            )
        ]
        return self.new("+", personnes)


def prop_records(compte: Compte) -> list[str]:
    lines = []
    for i, p in enumerate(compte.personnes, start=1):
        r = Record(700).text(1, 2, DEP).text(3, 1, DIR).text(4, 3, COM)
        r.text(7, 6, compte.dnupro).num(13, 2, i).text(15, 4, CCOCIF).text(19, 6, p.dnuper)
        r.text(25, 1, p.ccodro).text(26, 1, p.ccodem).text(27, 1, "1" if p.destinataire else "")
        r.text(28, 1, p.gtoper).text(29, 1, p.ccoqua)
        r.text(35, 3, p.dnatpr).text(38, 2, p.ccogrm).text(50, 4, p.dforme)
        if p.gtoper == "1":
            r.text(57, 60, f"{p.nom}/{p.prenom}")
        else:
            r.text(57, 60, p.denomination)

        # Address
        a = p.adresse
        # Lines: 3 empty, 4 formatted address, 5 empty, 6 code postal and commune
        r.text(117, 4, "9392")
        r.text(151, 36, a.dlign4()).text(217, 32, a.dlign6())
        if a.ccoriv:
            r.text(252, 2, DEP).text(254, 1, DIR).text(255, 3, COM)
            r.text(258, 5, ccovoi(a.ccoriv)).text(263, 4, a.ccoriv)
            r.text(267, 4, a.dnvoiri.rjust(4, "0"))
        r.text(272, 5, a.code_postal)

        if p.gtoper == "1":
            r.text(287, 3, "M" if p.ccoqua == "1" else "MME")
            r.text(290, 30, p.nom).text(320, 15, p.prenom)
            r.text(335, 10, p.naissance).text(345, 58, p.lieu_naissance)
            r.text(538, 60, p.nom).text(598, 40, p.prenom)
        else:
            r.text(467, 9, p.dsiren).text(534, 4, p.dformjur)
        lines.append(str(r))
    return lines


# ---------------------------------------------------------------- parcels


@dataclass
class Parcelle:
    geo_parcelle: str
    contenance: int
    nb_batiments: int
    surface_batie: int
    compte: Compte | None = None
    adresse: tuple | None = None  # (dnvoiri, ccoriv, nature, libelle)
    sufs: list = field(default_factory=list)  # (ccosub, contenance, cgrnum, classe)
    pdl: bool = False

    @property
    def ccosec(self) -> str:
        # The section is right aligned in MAJIC, "0A" in the EDIGEO identifier
        section = self.geo_parcelle[9:11]
        return " " + section[1] if section[0] == "0" else section

    @property
    def dnupla(self) -> str:
        return self.geo_parcelle[11:15]

    @property
    def proprietaire(self) -> Compte:
        """The owner, once set by build()"""
        if self.compte is None:
            raise ValueError(f"No owner for the parcel {self.geo_parcelle}")
        return self.compte

    @property
    def voie(self) -> tuple:
        """The address (dnvoiri, ccoriv, nature, libelle), once set by build()"""
        if self.adresse is None:
            raise ValueError(f"No address for the parcel {self.geo_parcelle}")
        return self.adresse


def read_parcelles() -> list[Parcelle]:
    with open(HERE / "parcelles_edigeo_13029.csv") as f:
        return [
            Parcelle(row["geo_parcelle"], int(row["contenance"]), int(row["nb_batiments"]), int(row["surface_batie"]))
            for row in csv.DictReader(f, delimiter=";")
        ]


def nbat_parcelle(p: Parcelle) -> list[str]:
    lines = []
    r = Record(200).text(1, 2, DEP).text(3, 1, DIR).text(4, 3, COM)
    r.text(10, 2, p.ccosec).text(12, 4, p.dnupla).text(20, 2, "10")
    r.num(22, 9, p.contenance).text(32, 6, p.proprietaire.dnupro)
    r.text(38, 8, f"{rng.randint(1, 28):02d}{rng.randint(1, 12):02d}{rng.randint(1975, 2025)}")
    r.text(51, 1, "1" if p.pdl else "0")
    if p.pdl:
        r.text(55, 2, p.ccosec).text(57, 4, p.dnupla).text(61, 3, "001")
    r.text(64, 1, "U" if p.nb_batiments else "").text(70, 1, "1").text(71, 1, "1" if p.nb_batiments else "")
    dnvoiri, ccoriv, natvoi, libvoi = p.voie
    r.text(86, 4, dnvoiri.rjust(4, "0") if dnvoiri else "").text(91, 5, ccovoi(ccoriv)).text(96, 4, ccoriv)
    r.text(100, 4, CCOCIF).text(122, 3, CCPPER).text(136, 4, natvoi).text(140, 26, libvoi)
    lines.append(str(r))

    for ccosub, contenance, cgrnum, classe in p.sufs:
        # Revenu cadastral by hectare, in centimes, depending on the culture
        tarif = {"01": 2200, "03": 4500, "04": 5200, "05": 600, "06": 300, "09": 9000, "13": 0}[cgrnum]
        drcsub = contenance * tarif // 10000
        r = Record(200).text(1, 2, DEP).text(3, 1, DIR).text(4, 3, COM)
        r.text(10, 2, p.ccosec).text(12, 4, p.dnupla).text(16, 2, ccosub).text(20, 2, "21")
        r.num(22, 9, contenance).text(31, 6, p.proprietaire.dnupro)
        r.num(39, 10, drcsub).num(49, 10, drcsub * 497 // 100)
        r.text(59, 1, "A").text(60, 2, cgrnum).text(64, 2, classe)
        r.text(71, 1, "0").num(148, 3, int(COM))
        lines.append(str(r))

        # Exoneration for the olive trees (vergers)
        if cgrnum == "03":
            r = Record(200).text(1, 2, DEP).text(3, 1, DIR).text(4, 3, COM)
            r.text(10, 2, p.ccosec).text(12, 4, p.dnupla).text(16, 2, ccosub).text(18, 2, "01")
            r.text(20, 2, "30").text(32, 2, "C").num(34, 5, 10000).text(39, 2, "OL")
            r.text(41, 4, "2020").text(45, 4, "2030").num(79, 10, drcsub * 497 // 100)
            lines.append(str(r))

        # Taxation: commune, departement (empty), TSE, groupement de communes
        r = Record(200).text(1, 2, DEP).text(3, 1, DIR).text(4, 3, COM)
        r.text(10, 2, p.ccosec).text(12, 4, p.dnupla).text(16, 2, ccosub).text(20, 2, "36")
        base = 0 if cgrnum == "03" else drcsub * 497 // 100
        for i in range(4):
            r.num(23 + 22 * i, 10, 0).num(34 + 22 * i, 10, 0 if i == 1 else base)
        lines.append(str(r))
    return lines


# ---------------------------------------------------------------- buildings


@dataclass
class Local:
    invar: str
    parcelle: Parcelle
    compte: Compte
    type: str  # MA maison, AP appartement, DE dependance
    surface: int
    pieces: int = 0
    dnubat: str = "A"
    descr: str = "01"
    dniv: str = "00"
    dpor: str = "01001"
    dependances: list = field(default_factory=list)  # (cconad, surface)
    lot: str = ""
    # A 2nd PEV (garage) and 2 exonerations on the 1st PEV, without random values
    multiple_pev: bool = False


invariants: set[str] = set()


def invariant() -> str:
    while True:
        value = COM + f"{rng.randint(0, 9999999):07d}"
        if value not in invariants:
            invariants.add(value)
            return value


def bati_records(local: Local) -> list[str]:
    p = local.parcelle
    dnvoiri, ccoriv, natvoi, libvoi = p.voie
    # About 5 % of recent houses, still exonerated
    jannat = rng.randint(2024, 2025) if local.type == "MA" and rng.random() < 0.05 else rng.randint(1890, 2022)
    lines = []

    def record(cenr: str, dnupev: str = "") -> Record:
        r = Record(200).text(1, 2, DEP).text(3, 1, DIR).text(4, 3, COM).text(7, 10, local.invar)
        return r.text(28, 3, dnupev).text(31, 2, cenr)

    # 00: identification of the local
    r = record("00").text(39, 2, p.ccosec).text(41, 4, p.dnupla)
    r.text(46, 2, local.dnubat).text(48, 2, local.descr).text(50, 2, local.dniv).text(52, 5, local.dpor)
    r.text(57, 4, ccoriv).text(62, 5, ccovoi(ccoriv)).text(67, 4, dnvoiri.rjust(4, "0") if dnvoiri else "")
    r.text(72, 4, CCOCIF).text(76, 30, f"{natvoi} {libvoi}".strip()).text(106, 1, rng.choice("ABCDEFGHJK"))
    r.text(125, 3, CCPPER)
    lines.append(str(r))

    # 10: description of the local
    dteloc = {"MA": "1", "AP": "2", "DE": "3"}[local.type]
    dvltrt = local.surface * rng.randint(30, 60)
    r = record("10").text(36, 1, "1" if local.lot else "0").text(38, 6, local.compte.dnupro)
    r.text(44, 8, f"{rng.randint(1, 28):02d}{rng.randint(1, 12):02d}{rng.randint(1980, 2025)}")
    r.text(58, 1, "C").text(60, 1, dteloc).text(61, 2, "P ").text(67, 2, local.type)
    r.num(69, 9, dvltrt).text(94, 1, "P" if local.type != "DE" else "")
    r.text(109, 4, str(jannat)).num(113, 2, 1 if local.type == "AP" else rng.randint(1, 2))
    r.text(149, 1, "").text(174, 1, "0")
    lines.append(str(r))

    # 21: PEV, habitation or dependance
    dcapec = f"{rng.randint(4, 7):02d}"
    r = record("21", "001").text(36, 1, "H").text(37, 1, "A").text(38, 2, dcapec).num(40, 3, 100)
    r.num(55, 6, local.surface).num(61, 9, dvltrt * 100 // 497).num(70, 9, dvltrt)
    r.text(111, 1, "P").num(144, 1, 1).num(145, 3, int(COM))
    lines.append(str(r))

    # 30: exoneration of the recent houses, 2 years for a new construction
    if local.type == "MA" and jannat >= 2024 and not local.multiple_pev:
        r = record("30", "001").text(24, 4, ANNEE).text(33, 3, "001").text(36, 2, "C").num(38, 5, 10000)
        r.text(43, 2, "ND").text(45, 4, str(jannat + 1)).text(49, 4, str(jannat + 3))
        r.num(93, 9, dvltrt // 2).num(143, 9, dvltrt // 2)
        lines.append(str(r))

    # 36: taxation of the PEV, commune, (empty), TSE, groupement de communes
    r = record("36", "001")
    base = dvltrt // 2
    for i, start in enumerate((36, 66, 96, 126)):
        if i != 1:
            r.num(start, 9, dvltrt * 100 // 497).num(start + 10, 9, dvltrt).num(start + 20, 9, base)
    r.num(156, 9, base).num(166, 9, base)
    lines.append(str(r))

    if local.type in ("MA", "AP"):
        # 40: main part of the habitation
        r = record("40", "001").text(33, 3, "001")
        for i, (cconad, surface) in enumerate(local.dependances[:4]):
            r.text(36 + 10 * i, 2, cconad).num(38 + 10 * i, 6, surface).num(44 + 10 * i, 2, 5)
        r.text(76, 8, "OOONOONO" if local.type == "MA" else "OOOOOOON")
        r.num(84, 2, 1).num(86, 2, 1).num(88, 2, 2).num(90, 2, 1).num(92, 3, 12)
        chambres = max(local.pieces - 1, 1)
        r.num(95, 2, local.pieces).num(97, 2, 1).num(99, 2, chambres).num(101, 2, 0).num(103, 2, 1)
        r.num(105, 2, 1).num(107, 2, 0).num(109, 2, local.pieces + 2).num(111, 6, local.surface)
        r.text(117, 2, rng.choice(["01", "03", "04"])).text(119, 2, "01").text(121, 4, str(jannat))
        r.text(125, 1, str(rng.randint(1, 3))).num(126, 2, 1 if local.type == "AP" else rng.randint(1, 2))
        lines.append(str(r))
    else:
        # 60: isolated dependance
        cconad, surface = local.dependances[0]
        r = record("60", "001").text(33, 3, "001").num(36, 6, surface).text(42, 2, cconad)
        r.text(50, 2, "03").text(52, 2, "01").text(54, 1, "2").text(55, 3, "NON")
        r.num(69, 2, 6).num(71, 3, 100)
        lines.append(str(r))

    if local.multiple_pev:
        lines += multiple_pev_records(record, dvltrt)
    return lines


def multiple_pev_records(record, dvltrt: int) -> list[str]:
    """Exonerations by the commune (100 %) and the groupement (50 %) of the 1st PEV, and a garage in a 2nd PEV"""
    lines = []
    for dnuexb, ccolloc, pexb in (("001", "C", 10000), ("002", "GC", 5000)):
        fraction = dvltrt * pexb // 10000
        r = record("30", "001").text(24, 4, ANNEE).text(33, 3, dnuexb).text(36, 2, ccolloc).num(38, 5, pexb)
        r.text(43, 2, "ND").text(45, 4, "2025").text(49, 4, "2027")
        r.num(93, 9, fraction // 2).num(133, 9, fraction).num(143, 9, fraction // 2)
        lines.append(str(r))

    surface, dvlpera = 18, 720
    r = record("21", "002").text(36, 1, "H").text(37, 1, "A").text(38, 2, "06").num(40, 3, 100)
    r.num(55, 6, surface).num(61, 9, dvlpera * 100 // 497).num(70, 9, dvlpera)
    r.text(111, 1, "P").num(144, 1, 1).num(145, 3, int(COM))
    lines.append(str(r))

    r = record("36", "002")
    for i, start in enumerate((36, 66, 96, 126)):
        if i != 1:
            r.num(start, 9, dvlpera * 100 // 497).num(start + 10, 9, dvlpera).num(start + 20, 9, dvlpera // 2)
    r.num(156, 9, dvlpera // 2).num(166, 9, dvlpera // 2)
    lines.append(str(r))

    r = record("60", "002").text(33, 3, "001").num(36, 6, surface).text(42, 2, "GA")
    r.text(50, 2, "03").text(52, 2, "01").text(54, 1, "2").text(55, 3, "NON")
    r.num(69, 2, 6).num(71, 3, 100)
    lines.append(str(r))
    return lines


# ---------------------------------------------------------------- PDL


def pdll_records(p: Parcelle, lots: list[tuple[str, Local, int, int]]) -> list[str]:
    """Copropriete: one PDL with lots. lots = (dnulot, local, numerator, denominator)"""

    def identifiant(dnulot: str = "") -> Record:
        r = Record(100).text(1, 2, DEP).text(3, 1, DIR).text(4, 3, COM)
        return r.text(10, 2, p.ccosec).text(12, 4, p.dnupla).text(16, 3, "001").text(19, 7, dnulot)

    lines = []
    r = identifiant().text(26, 2, "10").text(28, 1, "1").text(29, 3, "CL")
    r.text(62, 20, "LE CLOS DES OLIVIERS").text(83, 6, p.proprietaire.dnupro).text(94, 4, CCOCIF)
    lines.append(str(r))
    for dnulot, local, numerateur, denominateur in lots:
        r = identifiant(dnulot).text(26, 2, "30").text(28, 1, "2")
        r.num(38, 7, numerateur).num(45, 7, denominateur)
        r.text(72, 8, f"{rng.randint(1, 28):02d}{rng.randint(1, 12):02d}{rng.randint(1995, 2025)}")
        r.text(83, 6, local.compte.dnupro).text(94, 4, CCOCIF)
        lines.append(str(r))
    return lines


def lloc_records(p: Parcelle, lots: list[tuple[str, Local, int, int]]) -> list[str]:
    lines = []
    for dnulot, local, numerateur, denominateur in lots:
        r = Record(60).text(1, 2, DEP).text(3, 1, DIR).text(4, 3, COM)
        r.text(10, 2, p.ccosec).text(12, 4, p.dnupla).text(16, 3, "001").text(19, 7, dnulot)
        r.text(28, 2, DEP).text(30, 1, DIR).text(31, 3, COM).text(37, 10, local.invar)
        r.num(47, 7, numerateur).num(54, 7, denominateur)
        lines.append(str(r))
    return lines


# ---------------------------------------------------------------- data set


def build():
    parcelles = read_parcelles()
    comptes = Comptes()

    commune = comptes.morale(
        "COMMUNE DE CORNILLON-CONFOUX", "4", "7210", "COM", dnatpr="CLL", dsiren="211300298",
        adresse=Adresse("1", "PL", "DE LA MAIRIE", CODE_POSTAL, "CORNILLON CONFOUX", ""),
    )
    departement = comptes.morale(
        "DEPARTEMENT DES BOUCHES-DU-RHONE", "3", "7220", "DEPT", dnatpr="CLL", dsiren="221300015",
        adresse=Adresse("52", "AV", "DE SAINT JUST", "13004", "MARSEILLE"),
    )
    sci = comptes.morale("SCI LES OLIVIERS DE CONFOUX", "0", "6540", "SCI", dsiren="902154378")
    gfa = comptes.morale("GFA DU DOMAINE DE BELVEZET", "0", "6534", "GFA", dsiren="410287965")
    copropriete = comptes.morale(
        "COPROPRIETE LE CLOS DES OLIVIERS", "7", "F001", "", ccodro="P",
    )
    # The syndic of the copropriete receives the tax notices
    syndic = Personne(
        dnuper=dnuper("P"), gtoper="2", ccodro="S", denomination="PROVENCE GESTION IMMOBILIERE",
        ccogrm="0", dforme="5499", dformjur="SARL", dsiren="533812490", destinataire=True,
        adresse=Adresse("0003", "RUE", "DES CORDELIERS", "13100", "AIX EN PROVENCE"),
    )
    copropriete.personnes[0].destinataire = False
    copropriete.personnes.append(syndic)

    physiques = [comptes.physique() for _ in range(70)]

    batis = [p for p in parcelles if p.nb_batiments]
    non_batis = [p for p in parcelles if not p.nb_batiments]
    # The parcel with the largest building is the copropriete
    copro_parcelle = max(batis, key=lambda p: p.surface_batie)
    copro_parcelle.pdl = True
    copro_parcelle.compte = copropriete

    # Built parcels: one owner each, with an address on a voie
    for p in batis:
        if p.compte is None:
            p.compte = rng.choice([*physiques[:60], sci])
        ccoriv, natvoi, libvoi = rng.choice(VOIES)
        p.adresse = (str(rng.randint(1, 150)), ccoriv, natvoi, libvoi)
        sol = min(p.contenance, max(p.surface_batie, 20))
        p.sufs = [("", sol, "13", "")]
        if p.contenance - sol > 50:
            p.sufs = [("A", sol, "13", ""), ("B", p.contenance - sol, "09", "01")]

    # Not built parcels: big ones for public owners and agricultural owners
    for p in sorted(non_batis, key=lambda p: -p.contenance):
        if p.contenance > 40000:
            p.compte = rng.choice([commune, gfa, departement])
        elif p.contenance > 10000:
            p.compte = rng.choice([gfa, commune, *physiques[40:]])
        else:
            p.compte = rng.choice(physiques)
        ccoriv, libelle = rng.choice(LIEUX_DITS)
        p.adresse = ("", ccoriv, "", libelle)
        if p.contenance > 40000:
            cgrnum = rng.choice(["05", "06"])
        elif p.contenance > 10000:
            cgrnum = rng.choice(["04", "03", "05", "01"])
        else:
            cgrnum = rng.choice(["01", "03", "04", "06", "09"])
        p.sufs = [("", p.contenance, cgrnum, f"{rng.randint(1, 4):02d}")]

    # Buildings
    locaux: list[Local] = []
    lots = []
    for p in batis:
        if p is copro_parcelle:
            # 4 apartments and a garage, each lot has its owner
            for i in range(4):
                compte = rng.choice(physiques[60:])
                local = Local(
                    invariant(), p, compte, "AP", rng.randint(45, 95), pieces=rng.randint(2, 4),
                    dniv=f"{i // 2:02d}", dpor=f"0{i // 2}00{i % 2 + 1}", dependances=[("CV", 8)], lot=f"{i + 1:07d}",
                )
                locaux.append(local)
                lots.append((local.lot, local, 2400, 10000))
            local = Local(invariant(), p, copropriete, "DE", 15, dependances=[("GA", 15)], lot="0000005")
            locaux.append(local)
            lots.append((local.lot, local, 400, 10000))
            continue

        surface = max(min(p.surface_batie * rng.randint(70, 120) // 100, 250), 25)
        dependances = []
        if rng.random() < 0.4:
            dependances.append(("GA", rng.randint(12, 30)))
        if rng.random() < 0.15:
            dependances.append(("PS", rng.randint(24, 40)))
        locaux.append(Local(invariant(), p, p.compte, "MA", surface, pieces=rng.randint(3, 6), dependances=dependances))
        if p.nb_batiments > 1:
            # Isolated dependance: remise
            surface = rng.randint(10, 40)
            locaux.append(Local(invariant(), p, p.compte, "DE", surface, dnubat="B", dependances=[("RS", surface)]))

    # The first house has 2 PEV and 2 exonerations, for the fiche of the locaux
    next(local for local in sorted(locaux, key=lambda local: local.invar) if local.type == "MA").multiple_pev = True

    return parcelles, comptes, locaux, copro_parcelle, lots


def write():
    parcelles, comptes, locaux, copro_parcelle, lots = build()
    used = {p.proprietaire.dnupro for p in parcelles} | {local.compte.dnupro for local in locaux}

    def save(name: str, lines: list[str]):
        (OUTPUT / name).write_text("\n".join(lines) + "\n", encoding="ascii")

    prop = headers(700, 15, 45)
    for compte in sorted(comptes.comptes, key=lambda c: c.dnupro):
        if compte.dnupro in used:
            prop += prop_records(compte)
    save("REVPROP.800", prop)

    nbat = headers(200, 22, 52)
    for p in sorted(parcelles, key=lambda p: p.geo_parcelle):
        nbat += nbat_parcelle(p)
    save("REVNBAT.800", nbat)

    bati = headers(200, 36, 66)
    for local in sorted(locaux, key=lambda local: local.invar):
        bati += bati_records(local)
    save("REVBATI.800", bati)

    save("REVFPDL.800", headers(100, 28, 58) + pdll_records(copro_parcelle, lots))
    save("REVD166.800", lloc_records(copro_parcelle, lots))

    # Add the lieux-dits to the TOPO file
    topo = (OUTPUT / "TOPO_test.csv").read_text(encoding="utf-8").splitlines()
    existing = {line.split(";")[4] for line in topo[1:]}
    for code, libelle in LIEUX_DITS:
        if code in TOPO_NOUVEAUX_LIEUX_DITS and code not in existing:
            motclas = libelle.split(" ")[-1]
            topo.append(f"99100;93;13;029;{code};14;;{libelle};;;;;0;;00000000;19870101;3;{motclas};00000000")
    (OUTPUT / "TOPO_test.csv").write_text("\n".join(topo) + "\n", encoding="utf-8")

    print(
        f"{len(parcelles)} parcelles, {len(used)} comptes, {len(locaux)} locaux, "
        f"{len(lots)} lots dans la copropriété {copro_parcelle.geo_parcelle}"
    )


if __name__ == "__main__":
    write()
