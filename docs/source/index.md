# Welcome to pygeomhades's documentation!

Python package containing the Monte Carlo geometry implementation of the LEGEND
HPGe characterization test stand in HADES.

::: warning This package is currently in an early development stage! :::

This geometry can be used as an input to the
[remage](https://remage.readthedocs.io/en/stable/) simulation software.

This package is based on {doc}`pyg4ometry <pyg4ometry:index>`,
{doc}`legend-pygeom-hpges <legendhpges:index>` (implementation of HPGe
detectors) and {doc}`legend-pygeom-tools <pygeomtools:index>`.

## Installation

The latest tagged version and all its dependencies can be installed from PyPI:

```
pip install legend-pygeom-hades
```

Alternatively, the packages's development version can be installed from a git
checkout (in the directory of the git checkout):

```
pip install -e .
```

## Usage as CLI tool

After installation, the CLI utility `legend-pygeom-hades` is provided on your
`$PATH`. This CLI utility is the primary way to interact with this package. For
now, you can find usage docs by running:

```console
$ legend-pygeom-hades -h
```

In the simplest case, you can create a usable geometry file with:

```console
$ legend-pygeom-hades hades.gdml --config <...>
```

It is necessary to provide a config file describing the detector to simulate,
see {doc}`configuration` for more info.

## Extra metadata

Some additional metadata is needed to describe the vacuum cryostat test stand
geometry. This is described in {doc}`metadata`.

## Next steps

```{toctree}
:maxdepth: 1
:caption: User Manual

Configuration <configuration>
Extra metadata format <metadata>
Package API reference <api/modules>
```

## Related projects

- [legend-pygeom-hpges](https://github.com/legend-exp/legend-pygeom-hpges):
  high-purity germanium detector geometries for radiation transport simulations.
- [legend-pygeom-tools](https://github.com/legend-exp/legend-pygeom-tools):
  general-purpose tools for implementing and visualizing geometries.
- [legend-pygeom-l200](https://github.com/legend-exp/legend-pygeom-l200) and
  [legend-pygeom-l1000](https://github.com/legend-exp/legend-pygeom-l1000): the
  LEGEND-200 and LEGEND-1000 geometries for radiation transport simulations,
  useful examples of complex experimental setup implementations.
- [reboost](https://github.com/legend-exp/reboost): post-processing and analysis
  of remage output.
