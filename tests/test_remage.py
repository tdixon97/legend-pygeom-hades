from __future__ import annotations

import os

import dbetto
import pygeomtools
import pytest
from pathlib import Path
from pygeomhades import core

public_geom = os.getenv("LEGEND_METADATA", "") == ""

pytestmark = [
    pytest.mark.xfail(run=True, reason="requires a remage installation"),
    pytest.mark.needs_remage,
]


@pytest.fixture
def gdml_files(tmp_path):
    meta = dbetto.TextDB(f"{Path(__file__).parent}/dummy_prod/c1/")
    out = []

    for meas, runinfo in meta.items():
        info = next(iter(runinfo.values()))

        reg = core.construct(
            info,
            public_geometry=True,
        )

        gdml_file = tmp_path / f"hades-public-{meas}.gdml"
        pygeomtools.write_pygeom(reg, gdml_file)
        out.append(gdml_file)

    return out


def test_overlaps(gdml_files):
    from remage import remage_run

    macro = [
        "/RMG/Geometry/RegisterDetectorsFromGDML Germanium",
        "/run/initialize",
    ]
    for gdml_file in gdml_files:
        remage_run(macro, gdml_files=str(gdml_file), raise_on_error=True, raise_on_warning=True)
