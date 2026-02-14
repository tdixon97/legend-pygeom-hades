from __future__ import annotations

import logging
import tempfile
from collections.abc import Mapping
from pathlib import Path

from dbetto import AttrsDict
from pyg4ometry import gdml, geant4

log = logging.getLogger(__name__)


def parse_measurement(measurement: str) -> AttrsDict:
    """Parse a measurement string into its components.

    The measurement string is expected to be in the format
    `{source}_{HSX}_{position}_{ID}` eg. "am_HS1_top_dlt".

    For more details see [link](https://legend-exp.atlassian.net/wiki/spaces/LEGEND/pages/1826750480/Analysis+of+characterization+data+WIP).


    Parameters
    ----------
    measurement
        The measurement string, e.g., "am_HS1_top_dlt".

    Returns
    -------
    AttrsDict
        A dictionary with keys "source", "position", and "id" containing the parsed components of the measurement string.
        For example, for "am_HS1_top_dlt", the returned
        dictionary would be {"source": "am_HS1", "position": "top", "id": "dlt"}.
    """

    split = measurement.split("_")

    if len(split) != 4:
        msg = f"Measurement string '{measurement}' is not in the expected format '{{source_HSX}}_{{position}}_{{ID}}'."
        raise ValueError(msg)

    return AttrsDict({"source": split[0] + "_" + split[1], "position": split[2], "id": split[3]})


def merge_configs(diode_meta: AttrsDict, extra_meta: Mapping, *, extra_name: str = "hades") -> AttrsDict:
    """Merge the configs from `diode_meta` to the extra information
    provided in `extra_meta`.

    This also adds the needed `enrichment` value if this is not present.

    Parameters
    ----------
    diode_meta
        The standard metadata for the diode.
    extra_meta
        Extra metadata to add.
    extra_name
        name of the subdictionary to add the extra metadata to.
    """
    # make sure there is an enrichment value
    if diode_meta["production"]["enrichment"]["val"] is None:
        diode_meta["production"]["enrichment"]["val"] = 0.9  # reasonable value

    diode_meta[extra_name] = extra_meta

    return diode_meta


def read_gdml_with_replacements(
    dummy_gdml_path: Path, replacements: Mapping
) -> geant4.LogicalVolume | dict[str, geant4.LogicalVolume]:
    """Read a GDML file including replacements.

    Parameters
    ----------
    dummy_gdml_path
        path to the GDML template.
    replacements
        Constants in the GDML file to replace.
    """

    gdml_text = dummy_gdml_path.read_text()

    for key, val in replacements.items():
        gdml_text = gdml_text.replace(key, f"{val:.1f}")

    with tempfile.NamedTemporaryFile("w+", suffix=".gdml") as f:
        f.write(gdml_text)
        f.flush()

        reader = gdml.Reader(f.name)
        reg_tmp = reader.getRegistry()

    return reg_tmp.worldVolume
