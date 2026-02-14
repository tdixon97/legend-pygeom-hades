from __future__ import annotations


def test_cli():
    from pygeomhades.cli import _parse_cli_args

    args = _parse_cli_args(["--config", "test.yaml"])
    assert args is not None
