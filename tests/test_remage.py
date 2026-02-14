from __future__ import annotations

import os
from importlib import resources
from pathlib import Path

import dbetto
import pygeomtools
import pytest
from dbetto import AttrsDict
from pyg4ometry import geant4

from pygeomhades import core
from pygeomhades.core import construct

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

        pygeomtools.geometry.check_registry_sanity(reg, reg)

        pygeomtools.write_pygeom(reg, gdml_file)
        out.append(gdml_file)

    dets = Path(resources.files("pygeomhades") / "configs" / "holder_wrap").glob("*.yaml")

    # test for all detectors
    # only works for public geometry
    for det in dets:
        if public_geom:
            continue

        reg = construct(
            AttrsDict(
                {
                    "detector": str(det.stem),
                    "campaign": "c1",
                    "measurement": "am_HS1_top_dlt",
                    "daq_settings": AttrsDict({"flashcam": {"card_interface": "efb2"}}),
                }
            ),
            public_geometry=public_geom,
        )
        assert isinstance(reg, geant4.Registry)

        gdml_file = tmp_path / f"hades-public-{det.stem}.gdml"

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
        remage_run(
            macro,
            gdml_files=str(gdml_file),
            raise_on_error=True,
            raise_on_warning=True,
        )
