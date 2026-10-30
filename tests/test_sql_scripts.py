""" Static checks of the SQL scripts used by the import """

import re

from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent.parent / "cadastre" / "scripts" / "plugin"

# to_number(SUBSTRING(tmp, start, length), 'mask')
TO_NUMBER = re.compile(r"to_number\(SUBSTRING\(tmp,\s*(\d+),\s*(\d+)\)\s*,\s*'([^']*)'\)")


@pytest.mark.parametrize(
    "script", sorted(SCRIPTS.glob("*/majic3_formatage_donnees.sql")), ids=lambda path: path.parent.name
)
def test_to_number_masks(script: Path):
    """ The mask must have the length of the field, otherwise the last digits are lost """
    errors = [
        f"line {number}: SUBSTRING(tmp, {start}, {length}) with mask '{mask}'"
        for number, line in enumerate(script.read_text(encoding="utf-8").splitlines(), start=1)
        for start, length, mask in TO_NUMBER.findall(line)
        if len(mask) != int(length)
    ]
    assert not errors, "\n".join(errors)
