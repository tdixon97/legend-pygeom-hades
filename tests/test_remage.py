from __future__ import annotations

import os

import dbetto
import pygeomtools
import pytest

from pygeomhades import core

public_geom = os.getenv("LEGEND_METADATA", "") == ""

pytestmark = [
    pytest.mark.xfail(run=True, reason="requires a remage installation"),
    pytest.mark.needs_remage,
]


@pytest.fixture
def gdml_file(tmp_path):
    daq_settings = dbetto.AttrsDict({"flashcam": {"card_interface": "efb1"}})

    reg = core.construct(
        dbetto.AttrsDict(
            {
                "detector": "V07302A",  # this works since its larger than the test detector
                "campaign": "c1",
                "measurement": "am_HS6_top_dlt",
                "daq_settings": daq_settings,
            }
        ),
        assemblies=["hpge", "lead_castle"],
        public_geometry=True,
    )

    gdml_file = tmp_path / "hades-public.gdml"
    pygeomtools.write_pygeom(reg, gdml_file)

    return gdml_file


def test_overlaps(gdml_file):
    from remage import remage_run

    macro = [
        "/RMG/Geometry/RegisterDetectorsFromGDML Germanium",
        "/run/initialize",
    ]

    remage_run(macro, gdml_files=str(gdml_file), raise_on_error=True, raise_on_warning=True)
