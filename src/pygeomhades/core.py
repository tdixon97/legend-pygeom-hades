from __future__ import annotations

import contextlib
import logging
import math
from importlib import resources
from pathlib import Path

import numpy as np
import pygeomtools
from dbetto import AttrsDict, TextDB
from git import GitCommandError
from legendmeta import LegendMetadata
from pyg4ometry import geant4
from pygeomhpges import make_hpge

from pygeomhades import dimensions as dim
from pygeomhades.create_volumes import (
    create_bottom_plate,
    create_cryostat,
    create_holder,
    create_lead_castle,
    create_source,
    create_source_holder,
    create_th_plate,
    create_vacuum_cavity,
    create_wrap,
)
from pygeomhades.metadata import PublicMetadataProxy
from pygeomhades.utils import merge_configs, parse_measurement

log = logging.getLogger(__name__)


DEFAULT_ASSEMBLIES = {"hpge", "source", "lead_castle"}


def _place_pv(
    lv: geant4.LogicalVolume,
    name: str,
    mother_lv: geant4.LogicalVolume,
    reg: geant4.Registry,
    *,
    x_in_mm: float = 0,
    y_in_mm: float = 0,
    z_in_mm: float = 0,
    x_rot: float = 0,
    invert_z_axes: bool = False,
) -> geant4.PhysicalVolume:
    """Wrapper to place the physical volume more concisely."""

    rot = [0, np.pi, 0, "rad"] if invert_z_axes else [x_rot, 0, 0, "rad"]

    return geant4.PhysicalVolume(
        rot,
        [x_in_mm, y_in_mm, z_in_mm, "mm"],
        lv,
        name.replace("_lv", ""),  # strip _lv from name
        mother_lv,
        registry=reg,
    )


def construct(
    config: AttrsDict,
    extra_meta: TextDB | Path | str | None = None,
    public_geometry: bool = False,
) -> geant4.Registry:
    """Construct the HADES geometry.

    Returns the registry containing the world volume.

    Parameters
    ----------
    config

    config
      configuration dictionary defining the geometry, e.g.,

      .. code-block:: yaml

          detector: V13049A
          daq_settings:
            flashcam:
              card_interface: efb2
          run: run0001
          measurement: th_HS2_top_psa
          source_position:
            phi_in_deg: 0.0
            r_in_mm: 0.0
            z_in_mm: 38.0

    extra_meta
        Extra metadata needed to construct the geometry (or a path to it). If
        `None` then this is taken as `pygeomhades/configs/holder_wrap`.
    public_geometry
      if true, uses the public geometry metadata instead of the LEGEND-internal
      legend-metadata.
    """

    hpge_name = config.detector
    measurement = config.measurement
    source_pos = config.get("source_position", None)
    run = config.get("run", None)
    table = int(config.daq_settings.flashcam.card_interface[-1])

    if extra_meta is None:
        extra_meta = TextDB(resources.files("pygeomhades") / "configs" / "holder_wrap")
    elif not isinstance(extra_meta, TextDB):
        extra_meta = TextDB(extra_meta)

    lmeta = None
    if not public_geometry:
        with contextlib.suppress(GitCommandError):
            lmeta = LegendMetadata(lazy=True)

    # require user action to construct a testdata-only geometry (i.e. to avoid accidental creation of "wrong"
    # geometries by LEGEND members).
    if lmeta is None and not public_geometry:
        msg = "cannot construct geometry from public testdata only, if not explicitly instructed"
        raise RuntimeError(msg)

    if lmeta is None:
        log.warning("CONSTRUCTING GEOMETRY FROM PUBLIC DATA ONLY")
        lmeta = PublicMetadataProxy()

    # extract the measurement info
    measurement_info = parse_measurement(measurement)

    position = measurement_info.position
    source_type = measurement_info.source
    diode_meta = lmeta.hardware.detectors.germanium.diodes[hpge_name]
    hpge_meta = merge_configs(diode_meta, extra_meta[hpge_name])

    reg = geant4.Registry()

    # Create the world volume
    world = geant4.solid.Box("world", 20, 20, 20, reg, "m")
    world_lv = geant4.LogicalVolume(world, "G4_Galactic", "world_lv", reg)
    reg.setWorld(world_lv)

    # place a box rotated 180 deg so the geometry is not upside down
    lab = geant4.solid.Box("lab", 18, 18, 18, reg, "m")
    lab_lv = geant4.LogicalVolume(lab, "G4_AIR", "lab_lv", reg)
    lab_lv.pygeom_color_rgba = False

    _place_pv(lab_lv, "lab_lv", world_lv, reg, invert_z_axes=True)

    # extract the metadata on the cryostat
    cryostat_meta = dim.get_cryostat_metadata(
        hpge_meta.type, hpge_meta.production.order, hpge_meta.production.slice
    )

    cavity_lv = create_vacuum_cavity(cryostat_meta, reg)
    cavity_lv.pygeom_color_rgba = False

    _place_pv(cavity_lv, "cavity_pv", lab_lv, reg, z_in_mm=cryostat_meta.position_cavity_from_top)

    # construct the mylar wrap
    wrap_lv = create_wrap(hpge_meta.hades.wrap.geometry, from_gdml=True)
    wrap_lv.pygeom_color_rgba = [0.0, 0.8, 0.2, 0.3]

    z_pos = hpge_meta.hades.wrap.position - cryostat_meta.position_cavity_from_top
    pv = _place_pv(wrap_lv, "wrap_pv", cavity_lv, reg, z_in_mm=z_pos)
    reg.addVolumeRecursive(pv)

    # construct the holder
    holder_lv = create_holder(
        hpge_meta.hades.holder.geometry, hpge_meta.type, hpge_meta.production.order, from_gdml=True
    )
    holder_lv.pygeom_color_rgba = [0.0, 0.8, 0.2, 0.3]

    z_pos = hpge_meta.hades.holder.position - cryostat_meta.position_cavity_from_top
    pv = _place_pv(holder_lv, "holder_pv", cavity_lv, reg, z_in_mm=z_pos)
    reg.addVolumeRecursive(pv)

    # construct the hpge, for now do not allow cylindrical asymmetry
    detector_lv = make_hpge(hpge_meta, name=hpge_meta.name, registry=reg, allow_cylindrical_asymmetry=False)
    detector_lv.pygeom_color_rgba = [0.33, 0.33, 0.33, 1.0]

    # an extra offset is needed to account for the different reference point
    # this is the top of the crystal in the original GDML but it's the p+ contact here

    extra_offset = max(detector_lv.get_profile()[1])
    z_pos = hpge_meta.hades.detector.position - cryostat_meta.position_cavity_from_top + extra_offset

    # we need to flip the detector axes when placing it in the cryostat
    pv = _place_pv(detector_lv, hpge_meta.name, cavity_lv, reg, z_in_mm=z_pos, invert_z_axes=True)

    # register the detector info for remage
    pv.set_pygeom_active_detector(
        pygeomtools.RemageDetectorInfo(
            "germanium",
            1,  # detector id in remage.
            hpge_meta,
        )
    )
    # construct the cryostat
    cryo_lv = create_cryostat(cryostat_meta, from_gdml=True)
    cryo_lv.pygeom_color_rgba = [0.0, 0.2, 0.8, 0.3]

    pv = _place_pv(cryo_lv, "cryo_pv", lab_lv, reg)
    reg.addVolumeRecursive(pv)

    if "source_position" in config:
        if source_pos is None:
            msg = "requested a geometry with source but no source position information was provided"
            raise RuntimeError(msg)

        if source_type not in ["am_HS1", "th_HS2"] and position == "lat":
            msg = f"lateral position not implemented for source type {source_type}"
            raise NotImplementedError(msg)

        source_dims = dim.get_source_metadata(source_type, position)
        holder_dims = dim.get_source_holder_metadata(source_type, position)

        source_lv = create_source(source_type, source_dims, holder_dims, from_gdml=True)

        source_position = translate_to_detector_frame(
            source_pos.phi_in_deg, source_pos.r_in_mm, source_pos.z_in_mm, source_type
        )

        # source position in the detector frame
        x_pos, y_pos, z_pos = source_position
        source_y_pos = y_pos
        source_z_pos = z_pos

        if source_type == "th_HS2":
            if position == "top":
                source_z_pos = -(
                    z_pos
                    + holder_dims.source.top_plate_height / 2
                    + source_dims.copper.height
                    + source_dims.copper.bottom_height
                )
                z_pos_plates = -(
                    z_pos + holder_dims.source.top_plate_height / 2 - source_dims.plates.height / 2
                )
                z_pos_holder = -(z_pos + holder_dims.source.top_plate_height / 2)

                # add plate
                th_plate_lv = create_th_plate(source_dims, from_gdml=True)
                pv = _place_pv(th_plate_lv, "th_plate_pv", lab_lv, reg, z_in_mm=z_pos_plates)
                reg.addVolumeRecursive(pv)

            elif position == "lat":  # lat
                source_y_pos = holder_dims.outer_width / 2 + source_dims.copper.bottom_height
                z_pos_holder = z_pos

            else:
                msg = f" position {position} not implemented."
                raise NotImplementedError(msg)

        elif source_type == "am_HS1":
            source_z_pos = -(z_pos + source_dims.collimator.height / 2)

        elif source_type in {"co_HS5", "ba_HS4", "am_HS6"}:
            z_pos_holder = -(z_pos + holder_dims.source.top_plate_height / 2)
            source_z_pos = -z_pos

        else:
            msg = f" Source type {source_type} not implemented."
            raise NotImplementedError(msg)

        pv = _place_pv(
            source_lv,
            "source_pv",
            lab_lv,
            reg,
            x_in_mm=x_pos,
            y_in_mm=source_y_pos,
            z_in_mm=source_z_pos,
            x_rot=0 if (position != "lat" or source_type != "th_HS2") else -np.pi / 2,
        )
        reg.addVolumeRecursive(pv)
        reg.logicalVolumeDict[source_lv.name].pygeom_color_rgba = [0.66, 0.44, 0.26, 0.5]
        reg.logicalVolumeDict["Source"].pygeom_color_rgba = [1, 0, 0, 0.9]

        if source_type != "am_HS1":
            s_holder_lv = create_source_holder(
                source_type,
                holder_dims,
                source_z=z_pos,
                meas_type=position,
                from_gdml=True,
            )
            s_holder_lv.pygeom_color_rgba = [0, 1, 1, 0.2]

            pv = _place_pv(s_holder_lv, "source_holder_pv", lab_lv, reg, z_in_mm=z_pos_holder)
            reg.addVolumeRecursive(pv)

    # construct lead castle and bottom plate

    if source_type != "am_HS1":  # for am_HS1 the castle and plate are not present
        plate_meta = dim.get_bottom_plate_metadata()
        plate_lv = create_bottom_plate(plate_meta, from_gdml=True)
        plate_lv.pygeom_color_rgba = [0.2, 0.3, 0.5, 0.05]

        z_pos = cryostat_meta.position_from_bottom + plate_meta.height / 2.0
        pv = _place_pv(plate_lv, "plate_pv", lab_lv, reg, z_in_mm=z_pos)
        reg.addVolumeRecursive(pv)

        # FIXME:
        # it seems that at the beginning, when tables 1 and 2 were still
        # different, the card interference didn't match the table yet because
        # during the buildup of the stations and lead castle it might have been
        # possible that Yoann replugged the stations. So it isn't so
        # straightforward to get the initial table info by looking at the cards
        if hpge_name in {"V02160B", "V02166B"} or (
            hpge_name == "V02160A"
            and measurement == "th_HS2_lat_psa"
            and run in {"r002", "r003", "r004", "r005"}
        ):
            table = 2
        else:
            table = 1

        castle_dims = dim.get_castle_dimensions(table)
        castle_lv = create_lead_castle(table, castle_dims, from_gdml=True)
        castle_lv.pygeom_color_rgba = [0.2, 0.3, 0.5, 0.05]

        z_pos = cryostat_meta.position_from_bottom - castle_dims.base.height / 2.0
        pv = _place_pv(castle_lv, "castle_pv", lab_lv, reg, z_in_mm=z_pos)
        reg.addVolumeRecursive(pv)

    return reg


def translate_to_detector_frame(
    phi: float, r: float, z: float, source_type: str
) -> list[float, float, float]:
    """Translate the source position from metadata to detector frame

    In most cases this is purely a translation from cylindrical to Cartesian coordinates, but for the am_HS1 source there is an extra offset in r that is not well known.

    Parameters
    ----------
    phi
        the phi position of the source in degrees, as given in the metadata
    r
        the r position of the source in mm, as given in the metadata
    z
        the z position of the source in mm, as given in the metadata
    source_type
        the type of source, as given in the metadata, e.g., "am_HS1"

    Returns
    -------
    x_position
        the x position of the source in mm in the detector frame
    y_position
        the y position of the source in mm in the detector frame
    z_position
        the z position of the source in mm in the detector frame

    """

    if source_type == "am_HS1" and r != 0:
        r += -66  # update this condition
        if r < 0:
            phi += 180
            r = abs(r)

        msg = "Translation to detector from for am_HS1 and r!=0 is uncertain. Proceed with caution."
        log.warning(msg)

    phi = phi * math.pi / 180.0
    x_position = round(r * math.cos(phi), 2)
    y_position = round(-r * math.sin(phi), 2)

    return [x_position, y_position, z]
