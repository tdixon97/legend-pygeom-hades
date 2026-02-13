from __future__ import annotations

import os

import pygeomtools
import pytest
from pyg4ometry import geant4

from dbetto import AttrsDict

from pygeomhades.core import construct

public_geom = os.getenv("LEGEND_METADATA", "") == ""


def test_import():
    import pygeomhades  # noqa: F401


def test_construct():
    # test for a bege
    reg = construct(
        AttrsDict({"hpge_name": "B00000B", "campaign": "c1", "measurement": "am_HS1_top_dlt"}),
        public_geometry=True,
    )
    assert isinstance(reg, geant4.Registry)
    pygeomtools.geometry.check_registry_sanity(reg, reg)

    # test for table 2
    reg = construct(
        AttrsDict({"hpge_name": "V02160B", "campaign": "c1", "measurement": "am_HS1_top_dlt"}),
        public_geometry=True,
    )
    assert isinstance(reg, geant4.Registry)
    pygeomtools.geometry.check_registry_sanity(reg, reg)

    with pytest.raises(NotImplementedError):
        # test for source assembly (not yet verified)
        _ = construct(
            AttrsDict(
                {
                    "hpge_name": "B00000B",
                    "campaign": "c1",
                    "measurement": "am_HS1_top_dlt",
                    "run": 1,
                }
            ),
            assemblies="hpge,lead_castle,source",
            public_geometry=True,
            construct_unverified=False,
        )
