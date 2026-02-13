from __future__ import annotations


def test_cli():
    from pygeomhades.cli import _parse_cli_args

    args = _parse_cli_args(["--detector", "V07302A", "--measurement", "am_HS1_top_dlt", "--run", "1"])
    assert args is not None
