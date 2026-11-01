""" Metadata of the plugin used from the sources, without packaging """

import pytest

from cadastre.plausible import ENV_SKIP_STATS, Plausible
from cadastre.tools import version


def test_version():
    # yapt-pkg replaces it with the version from pyproject.toml when packaging
    assert version() == "master"


@pytest.mark.parametrize("server", [False, True])
def test_no_stats_from_sources(monkeypatch: pytest.MonkeyPatch, server: bool):
    monkeypatch.delenv("CI", raising=False)
    monkeypatch.delenv(ENV_SKIP_STATS, raising=False)
    assert not Plausible(server=server).request_stat_event()
