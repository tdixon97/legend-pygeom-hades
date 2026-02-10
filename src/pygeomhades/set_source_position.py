from __future__ import annotations

import math
from typing import Any, Union
from pathlib import Path
from dbetto import TextDB

from pygeomhades.utils import parse_measurement

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
    details = "\n".join(f"{run}: {list(getattr(node, run).source_position.values())}" for run in node)
    if phi_position not in phi_pos:
        msg = ( 
            "Position ERROR. \n"
            f"Provided phi position [{phi_position}] not found in the database "
            f"for the given measurement {hpge_name}/{campaign}/{measurement}.\n"
            f"Available phi positions are: {phi_pos}\n"
            "\n"
            f"Full list of available runs, runXXXX: [phi, r, z]\n"
            f"{details}"
        )
        raise ValueError(msg)
    data = node.group("source_position.phi_in_deg").get(phi_position)
    r_available = []
    z_available = []
    matched_r = []
    for i in data:
        matched_z = False
        source_pos = data.get(i).get("source_position") or data.get("source_position")
        r_pos_ = source_pos.get("r_in_mm")
        if r_position != r_pos_:
            matched_r.append(False)
            if r_pos_ not in r_available:
                r_available.append(r_pos_)
            continue
        else:
            matched_r.append(True)   
        z_pos_ = source_pos.get("z_in_mm")
        if z_position != z_pos_:
            matched_z = False
            if z_pos_ not in z_available:
                z_available.append(z_pos_)
            continue
        else:
            matched_z = True
        run = data.get(i).get("run") or data.get("run")
    if not any(matched_r):
        msg = (
            "Position ERROR.\n"
            f"Provided r position [{r_position}] not found in the database "
            f"for the given measurement {hpge_name}/{campaign}/{measurement}.\n"
            f"For the provided phi position [{phi_position}], the available r positions are: {r_available}. \n"
            "\n"
            f"Full list of available runs, runXXXX: [phi, r, z]\n"
            f"{details}"
        )
        raise ValueError(msg)
    if not matched_z:
        msg = (
            "Position ERROR.\n"
            f"Provided z position [{z_position}] not found in the database "
            f"for the given measurement {hpge_name}/{campaign}/{measurement}.\n"
            f"For the provided phi position [{phi_position}] and r position [{r_position}], the available r positions are: {r_available}\n"
            "\n"
            "Full list of available runs, runXXXX: [phi, r, z]:\n"
            f"{details}"
        )
        raise ValueError(msg)
    return run


def set_source_position(
    hpge_name: str,
    measurement: str,
    campaign: str,
    run: int | None = None,
    source_pos: tuple[float, float, float] | None = None
) -> tuple[str, list, list]:
    """Return the run number and the source position in the lab_lv frame.

    Parameters
    ----------
    hpge_name
        Name of the detector, e.g., "V07302A".
    measurement
        Name of the measurement, e.g., "am_HS1_top_dlt".
    campaign
        Name of the campaign, e.g., "c1". 
    run
        Number of run, eg. "1" . 
    source_pos
        Source position, e.g. "0.0, 45.0, 3.0".
    """
    
    measurement_info = parse_measurement(measurement)
    position = measurement_info.position
    source_type = measurement_info.source

    metadata_path = Path(__file__).parents[2] / "hades-metadata" / "hardware" / "config"
    measurement_path = f"{metadata_path}/{hpge_name}/{campaign}/{measurement}"
    db = TextDB(metadata_path)

    try:
        node = db[hpge_name][campaign][measurement]
    except FileNotFoundError:
        msg = (
            f"The measurement {measurement_path} does not exist.\n"
            "Please check the configuration file and metadata."
        )
        raise ValueError(msg)

    details = "\n".join(f"{run}: {list(getattr(node, run).source_position.values())}" for run in node)

    if run is not None:  # the user knows the run number
        run = f"run{run:04d}"
        try:
            node = node[run]
        except AttributeError as e:
            msg(
                f"RUN ERROR.\n"
                f"Run '{run}' not found in the metadata. \n"
                f"Full list of available runs, runXXXX: [phi, r, z]\n"
                f"{details}"
            )
            raise ValueError(msg)
        phi_position = node.source_position.phi_in_deg
        r_position = node.source_position.r_in_mm
        z_position = node.source_position.z_in_mm
        run = run[:1] + run[4:]
    elif source_pos is not None:  # the user knows the source position
        run = check_source_position(node, source_pos, hpge_name, campaign, measurement)
        run = run[:1] + run[4:]
        phi_position, r_position, z_position = source_pos 
    else:
        msg = "Insert either run number or source position"
        raise ValueError(msg)
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
