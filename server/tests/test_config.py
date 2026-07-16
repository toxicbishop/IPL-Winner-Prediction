"""Tests for config.get_tournament_paths whitelist behavior."""

import pytest

from config import TOURNAMENTS, get_tournament_paths


def test_tournaments_has_ipl():
    assert "ipl" in TOURNAMENTS


def test_get_tournament_paths_valid_ipl():
    paths = get_tournament_paths("ipl")
    for key in ("matches", "features", "db", "results", "models"):
        assert key in paths
        assert isinstance(paths[key], str)
        assert paths[key]  # non-empty


@pytest.mark.parametrize("bad", ["", "IPL", "../etc/passwd", "ipl; rm -rf /", "unknown"])
def test_get_tournament_paths_rejects_invalid(bad):
    with pytest.raises(ValueError, match="Invalid tournament"):
        get_tournament_paths(bad)
