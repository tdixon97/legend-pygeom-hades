from __future__ import annotations

import os

import pygeomtools
from dbetto import AttrsDict
from pyg4ometry import geant4

from pygeomhades.core import construct, translate_to_detector_frame

public_geom = os.getenv("LEGEND_METADATA", "") == ""


def test_import():
    import pygeomhades  # noqa: F401


def test_construct():
    daq_settings = AttrsDict({"flashcam": {"card_interface": "efb1"}})
    # test for a bege
    reg = construct(
        AttrsDict(
            {
                "detector": "B00000B",
                "campaign": "c1",
                "measurement": "am_HS6_top_dlt",
                "daq_settings": daq_settings,
            }
        ),
        public_geometry=True,
    )
    assert isinstance(reg, geant4.Registry)
    pygeomtools.geometry.check_registry_sanity(reg, reg)

    # test for table 2
    daq_settings2 = AttrsDict({"flashcam": {"card_interface": "efb2"}})

    reg = construct(
        AttrsDict(
            {
                "detector": "V02160B",
                "campaign": "c1",
                "measurement": "am_HS6_top_dlt",
                "daq_settings": daq_settings2,
            }
        ),
        public_geometry=True,
    )

    # Copper plate should be present
    assert "Copper_plate_PV" in reg.physicalVolumeDict

    # test with source
    for meas in ["am_HS1_top_dlt", "th_HS2_top_dlt", "ba_HS4_top_dlt", "co_HS5_top_dlt", "am_HS6_top_dlt"]:
        pos = AttrsDict({"phi_in_deg": 0.0, "r_in_mm": 0.0, "z_in_mm": 38.0})

        reg = construct(
            AttrsDict(
                {
                    "detector": "V07302A",
                    "campaign": "c1",
                    "measurement": meas,
                    "daq_settings": daq_settings2,
                    "source_position": pos,
                }
            ),
            public_geometry=True,
        )

        assert isinstance(reg, geant4.Registry)
        pygeomtools.geometry.check_registry_sanity(reg, reg)

    # now lateral
    for meas in ["am_HS1_lat_dlt", "th_HS2_lat_psa"]:
        pos = AttrsDict({"phi_in_deg": 0.0, "r_in_mm": 30, "z_in_mm": 60.0})

        reg = construct(
            AttrsDict(
                {
                    "detector": "V07302A",
                    "campaign": "c1",
                    "measurement": meas,
                    "daq_settings": daq_settings2,
                    "source_position": pos,
                }
            ),
            public_geometry=True,
        )

        assert isinstance(reg, geant4.Registry)
        pygeomtools.geometry.check_registry_sanity(reg, reg)


def test_translate_to_detector_frame():
    # basic test for non HS1
    pos = AttrsDict({"phi_in_deg": 0.0, "r_in_mm": 0.0, "z_in_mm": 38.0})

    x, y, z = translate_to_detector_frame(
        pos.phi_in_deg, pos.r_in_mm, pos.z_in_mm, source_type="am_HS6_top_dlt"
    )

    assert x == 0.0
    assert y == 0.0
    assert z == 38.0
