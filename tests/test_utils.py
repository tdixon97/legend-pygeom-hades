from __future__ import annotations

from importlib import resources

import numpy as np
import pyg4ometry

from pygeomhades.metadata import PublicMetadataProxy
from pygeomhades.utils import get_profile, merge_configs, parse_measurement, read_gdml_with_replacements


def test_merge_config():
    meta = PublicMetadataProxy()

    hpge_meta = merge_configs(meta.hardware.detectors.germanium.diodes["V07302A"], {"dimensions": 1})

    assert hpge_meta.hades.dimensions == 1
    assert hpge_meta.production.enrichment.val is not None


def test_read_gdml_with_replacements():
    dummy_gdml_path = resources.files("pygeomhades") / "models" / "dummy" / "wrap_dummy.gdml"
    replacements = {
        "wrap_outer_height_in_mm": 100,
        "wrap_outer_radius_in_mm": 99,
        "wrap_inner_radius_in_mm": 98,
        "wrap_top_thickness_in_mm": 1,
    }

    lv = read_gdml_with_replacements(dummy_gdml_path, replacements)

    assert isinstance(lv, pyg4ometry.geant4.LogicalVolume)


def test_parse_measurement_basic():
    out = parse_measurement("cs_HS2_bottom_foo")

    assert out.source == "cs_HS2"
    assert out.position == "bottom"
    assert out.id == "foo"

    out = parse_measurement("am_HS1_top_dlt")

    assert out.source == "am_HS1"
    assert out.position == "top"
    assert out.id == "dlt"

    out = parse_measurement("am_HS6_top_dlt")

    assert out.source == "am_HS6"  # no renaming


def test_profile():
    reg = pyg4ometry.geant4.Registry()

    polycone = pyg4ometry.geant4.solid.Polycone(
        "test_polycone", 0, 2 * np.pi, [0, 10], [2, 10], [3, 10], lunit="mm", registry=reg
    )

    profile = get_profile(polycone)

    assert profile["r"] == [2, 10, 10, 3, 2]
    assert profile["z"] == [0, 10, 10, 0, 0]

    generic_polycone = pyg4ometry.geant4.solid.GenericPolycone(
        "test_generic_polycone",
        0,
        2 * np.pi,
        [0, 0, 10, 0],
        [2, 2, 5, 5],
        lunit="mm",
        registry=reg,
    )
    profile = get_profile(generic_polycone)
    assert profile["r"] == [0, 0, 10, 0, 0]
    assert profile["z"] == [2, 2, 5, 5, 2]
