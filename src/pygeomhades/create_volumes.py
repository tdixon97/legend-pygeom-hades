from __future__ import annotations

import numpy as np
from pyg4ometry import geant4

from pygeomhades import fixed_dimensions as dim
from pygeomhades.utils import _read_gdml_model

# TODO: These functions seem very repetitive, maybe there is a way to reduce
#      but maybe when/if we move away from loading gdml files this will not be true


def create_vacuum_cavity(reg: geant4.Registry) -> geant4.LogicalVolume:
    vacuum_cavity_radius = (dim.CRYOSTAT_WIDTH - 2 * dim.CRYOSTAT_THICKNESS) / 2
    vacuum_cavity_z = (
        dim.CRYOSTAT_HEIGHT - dim.POSITION_CRYOSTAT_CAVITY_FROM_TOP - dim.POSITION_CRYOSTAT_CAVITY_FROM_BOTTOM
    )
    cavity_material = geant4.MaterialPredefined("G4_AIR")
    vacuum_cavity = geant4.solid.GenericPolycone(
        "vacuum_cavity",
        0.0,
        2.0 * np.pi,
        pR=([0.0, vacuum_cavity_radius, vacuum_cavity_z, 0.0]),
        pZ=[0.0, 0.0, vacuum_cavity_z, vacuum_cavity_z],
        lunit="mm",
        aunit="rad",
        registry=reg,
    )
    return geant4.LogicalVolume(vacuum_cavity, cavity_material, "cavity_lv", reg)


def create_detector(from_gdml: bool = False) -> geant4.LogicalVolume:
    if from_gdml:
        reg_detector = _read_gdml_model("detector.gdml")
        detector_lv = reg_detector.getWorldVolume()
    else:
        # TODO: add the construction of geometry
        msg = "cannot construct geometry without the gdml for now"
        raise RuntimeError(msg)
    return detector_lv


def create_wrap(from_gdml: bool = False) -> geant4.LogicalVolume:
    if from_gdml:
        reg_wrap = _read_gdml_model("wrap.gdml")
        wrap_lv = reg_wrap.getWorldVolume()
    else:
        # TODO: add the construction of geometry
        msg = "cannot construct geometry without the gdml for now"
        raise RuntimeError(msg)
    return wrap_lv


def create_holder(from_gdml: bool = False) -> geant4.LogicalVolume:
    if from_gdml:
        reg_holder = _read_gdml_model("holder.gdml")
        holder_lv = reg_holder.getWorldVolume()
    else:
        # TODO: add the construction of geometry
        msg = "cannot construct geometry without the gdml for now"
        raise RuntimeError(msg)
    return holder_lv


def create_bottom_plate(from_gdml: bool = False) -> geant4.LogicalVolume:
    if from_gdml:
        reg_plate = _read_gdml_model("bottom_plate.gdml")
        plate_lv = reg_plate.getWorldVolume()
    else:
        # TODO: add the construction of geometry
        msg = "cannot construct geometry without the gdml for now"
        raise RuntimeError(msg)
    return plate_lv


def create_lead_castle(from_gdml: bool = False) -> geant4.LogicalVolume:
    if from_gdml:
        reg_castle = _read_gdml_model("lead_castle_table1.gdml")
        castle_lv = reg_castle.getWorldVolume()
    else:
        # TODO: add the construction of geometry
        msg = "cannot construct geometry without the gdml for now"
        raise RuntimeError(msg)
    return castle_lv


def create_source(from_gdml: bool = False) -> geant4.LogicalVolume:
    if from_gdml:
        # TODO: replace this with a generic reader?
        reg_source = _read_gdml_model("source_encapsulated_ba_HS4.gdml")
        source_lv = reg_source.getWorldVolume()
    else:
        # TODO: add the construction of geometry
        msg = "cannot construct geometry without the gdml for now"
        raise RuntimeError(msg)
    return source_lv


def create_source_holder(from_gdml: bool = False) -> geant4.LogicalVolume:
    if from_gdml:
        reg_s_holder = _read_gdml_model("plexiglass_source_holder.gdml")
        s_holder_lv = reg_s_holder.getWorldVolume()
    else:
        # TODO: add the construction of geometry
        msg = "cannot construct geometry without the gdml for now"
        raise RuntimeError(msg)
    return s_holder_lv


def create_cryostat(from_gdml: bool = False) -> geant4.LogicalVolume:
    if from_gdml:
        reg_cryo = _read_gdml_model("cryostat.gdml")
        cryo_lv = reg_cryo.getWorldVolume()
    else:
        # TODO: add the construction of geometry
        msg = "cannot construct geometry without the gdml for now"
        raise RuntimeError(msg)
    return cryo_lv
