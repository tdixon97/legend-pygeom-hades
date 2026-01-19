from __future__ import annotations

import logging
import pathlib
from importlib import resources

import pyg4ometry
from pyg4ometry import geant4

log = logging.getLogger(__name__)


def _read_gdml_model(file: str | pathlib.Path) -> geant4.Registry:
    file = resources.files("pygeomhades") / "models" / file
    reader = pyg4ometry.gdml.Reader(file)
    return reader.getRegistry()
