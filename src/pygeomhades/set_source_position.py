from __future__ import annotations

import math
import os
from typing import Any, Union

from dbetto import TextDB

from pygeomhades.utils import parse_measurement
SourceInfo = Union[int, tuple[float, float, float]]


def check_source_position(
    node: Any, user_positions: list[float], hpge_name: str, campaign: str, measurement: str
) -> Any:
    """Check the source position set by the user to those available in the metadata .

    Parameters
    ----------
    user_position
        source position, e.g. "0.0, 45.0, 3.0".
    hpge_name
        Name of the detector, e.g., "V07302A".
    measurement
        Name of the measurement, e.g., "am_HS1_top_dlt".
    campaign
        Name of the campaign, e.g., "c1". 
    """
  
    phi_position, r_position, z_position = user_positions[0], user_positions[1], user_positions[2]
    phi_pos = list(node.group("source_position.phi_in_deg").keys())
    details = "\n".join(f"{run}: {list(getattr(node, run).source_position.values())}" for run in node.keys())
    if phi_position not in phi_pos:
        raise ValueError(
            "Position ERROR. \n"
            f"Provided phi position [{phi_position}] not found in the database "
            f"for the given measurement {hpge_name}/{campaign}/{measurement}.\n"
            f"Available phi positions are: {phi_pos}\n"
            "\n"
            f"Full list of available runs, runXXXX: [phi, r, z]\n"
            f"{details}"
        )
    data = node.group("source_position.phi_in_deg").get(phi_position)
    r_available = []
    z_available = []
    matched_r = []
    for i in data.keys():
        matched_z = False
        try:
            r_pos_ = data.get(i).get("source_position").get("r_in_mm")
        except AttributeError:
            r_pos_ = data.get("source_position").get("r_in_mm")
        if r_position != r_pos_:
            matched_r.append(False)
            if r_pos_ not in r_available:
                r_available.append(r_pos_)
            continue
        matched_r.append(True)
        try:
            z_pos_ = data.get(i).get("source_position").get("z_in_mm")
        except AttributeError:
            z_pos_ = data.get("source_position").get("z_in_mm")
        if z_position != z_pos_:
            matched_z = False
            if z_pos_ not in z_available:
                z_available.append(z_pos_)
            continue
        matched_z = True
        try:
            run = data.get(i).get("run")
        except:
            run = data.get("run")
        return run
    if not any(matched_r):
        raise ValueError(
            "Position ERROR.\n"
            f"Provided r position [{r_position}] not found in the database "
            f"for the given measurement {hpge_name}/{campaign}/{measurement}.\n"
            f"For the provided phi position [{phi_position}], the available r positions are: {r_available}. \n"
            "\n"
            f"Full list of available runs, runXXXX: [phi, r, z]\n"
            f"{details}"
        )
    if matched_z == False:
        raise ValueError(
            "Position ERROR.\n"
            f"Provided z position [{z_position}] not found in the database "
            f"for the given measurement {hpge_name}/{campaign}/{measurement}.\n"
            f"For the provided phi position [{phi_position}] and r position [{r_position}], the available r positions are: {r_available}\n"
            "\n"
            "Full list of available runs, runXXXX: [phi, r, z]:\n"
            f"{details}"
        )


def set_source_position(
    hpge_name: str,
    measurement: str,
    campaign: str,
    source_info: SourceInfo,
) -> tuple[str, list, list]:
    MetaDataPath = "/global/cfs/cdirs/m2676/data/teststands/hades/prodenv/ref/v1.0.0/inputs/hardware/config"
    MeasurementPath = f"{MetaDataPath}/{hpge_name}/{campaign}/{measurement}.yaml"

    measurement_info = parse_measurement(measurement)

    position = measurement_info.position
    source_type = measurement_info.source
    
    db = TextDB(MetaDataPath)
    
    try:
        node = db[hpge_name][campaign][measurement]
    except FileNotFoundError:
        raise ValueError(
            f"The measurement {MeasurementPath} does not exist.\n"
            "Please check the configuration file and metadata."
        )

    details = "\n".join(f"{run}: {list(getattr(node, run).source_position.values())}" for run in node.keys())

    if isinstance(source_info, int):  # the user knows the run number
        run = f"run{source_info:04d}"
        try:
            node = node[run]
        except AttributeError:
            raise ValueError(
                f"RUN ERROR.\n"
                f"Run '{run}' not found in the metadata. \n"
                f"Full list of available runs, runXXXX: [phi, r, z]\n"
                f"{details}"
            )
        phi_position = node.source_position.phi_in_deg
        r_position = node.source_position.r_in_mm
        z_position = node.source_position.z_in_mm
        run = run[:1] + run[4:]
    else:  # the user knows the source position
        run = check_source_position(node, source_info, hpge_name, campaign, measurement)
        run = run[:1] + run[4:]

    if source_type == "am_HS1" and r_position != 0:  # update this condition
        r_position += -66
        if r_position < 0:
            phi_position += 180
            r_position = abs(r_position)
    phi = phi_position * math.pi / 180.0
    x_position = round(r_position * math.cos(phi), 2)
    y_position = round(-r_position * math.sin(phi), 2)

    # position in gdml file
    final_positions = [x_position, y_position, z_position]

    if position == "top":
        z_position = -z_position
    # position of radioactive source in .mac file
    macro_position = [x_position, y_position, z_position]
    if source_type == "ba_HS4":
        pass
    # check numbers below
    elif source_type == "th_HS2":
        if position == "top":
            macro_position[2] += -5.0  # (3.+.5+1.5)mm
        elif position == "lat":
            if macro_position[1] == 0:
                macro_position[1] = 82.3  # (60.8.+18.+3.+.5)mm
            else:
                macro_position[1] += 21.5  # (18.+3.+.5)mm
    elif source_type == "am_HS1":
        macro_position[2] += -26.8  # (25.6+0.2+1.) mm
    # else: #am_HS6
    # ListPosition[2]+= 1   #(25.6+0.2+1.) mm
    return run, final_positions, macro_position
