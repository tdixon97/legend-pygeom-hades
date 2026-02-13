from __future__ import annotations

import argparse
import logging

from dbetto import AttrsDict, utils
from pyg4ometry import config as meshconfig
from pygeomtools import geometry, write_pygeom

from . import _version, core

log = logging.getLogger(__name__)


def dump_gdml_cli(argv: list[str] | None = None) -> None:
    args = _parse_cli_args(argv)

    logging.basicConfig()
    if args.verbose:
        logging.getLogger("pygeomhades").setLevel(logging.DEBUG)
    if args.debug:
        logging.root.setLevel(logging.DEBUG)

    vis_scene = {}
    if isinstance(args.visualize, str):
        vis_scene = utils.load_dict(args.visualize)

    if args.clip_geometry:
        vis_scene["clipper"] = [{"origin": [0, 0, 0], "normal": [1, 0, 0], "close_cuts": False}]

    if vis_scene.get("fine_mesh", False) or args.check_overlaps:
        meshconfig.setGlobalMeshSliceAndStack(100)

    registry = core.construct(
        AttrsDict(
            {
                "hpge_name": args.hpge_name,
                "campaign": args.campaign,
                "measurement": args.measurement,
                "run": args.run,
                "source_pos": args.source_position,
            }
        ),
        assemblies=args.assemblies,
        public_geometry=args.public_geom,
    )

    if args.print_volumes:
        geometry.print_volumes(registry, args.print_volumes)

    if args.check_overlaps:
        msg = "checking for overlaps"
        log.info(msg)
        registry.worldVolume.checkOverlaps(recursive=True)

    # commit auxvals, and write to GDML file if requested.
    if args.filename is not None:
        log.info("exporting GDML geometry to %s", args.filename)
    write_pygeom(registry, args.filename)

    if args.visualize:
        log.info("visualizing...")
        from pygeomtools import viewer

        viewer.visualize(registry, vis_scene)


def _parse_cli_args(argv: list[str] | None = None) -> tuple[argparse.Namespace, dict]:
    parser = argparse.ArgumentParser(
        prog="legend-pygeom-hades",
        description="%(prog)s command line interface",
    )

    # global options
    parser.add_argument(
        "--version",
        action="version",
        help="""Print %(prog)s version and exit""",
        version=_version.__version__,
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="""Increase the program verbosity""",
    )
    parser.add_argument(
        "--debug",
        "-d",
        action="store_true",
        help="""Increase the program verbosity to maximum""",
    )
    parser.add_argument(
        "--visualize",
        "-V",
        nargs="?",
        const=True,
        help="""Open a VTK visualization of the generated geometry (with optional scene file)""",
    )
    parser.add_argument(
        "--clip-geometry",
        action="store_true",
        help="""Clip the geometry for visualization purposes""",
    )
    parser.add_argument(
        "--check-overlaps",
        action="store_true",
        help="""Check for overlaps with pyg4ometry (note: this might not be accurate)""",
    )
    parser.add_argument(
        "--print-volumes",
        action="store",
        choices=("logical", "physical", "detector"),
        help="""Print a list of logical or physical volume names (from the pyg4ometry registry)""",
    )

    # options for geometry generation.
    #
    # geometry options can also be specified in the config file, so the "default" argument of the argparse
    # options cannot be used - we need to distinguish between an unspecified option and an explicitly set
    # default option.
    geom_opts = parser.add_argument_group("geometry options")
    geom_opts.add_argument(
        "--public-geom",
        action="store_true",
        default=None,
        help="""Create a geometry from public testdata only.""",
    )
    geom_opts.add_argument(
        "--assemblies",
        action="store",
        default="hpge, source, lead_castle",
        help=(
            """Select the assemblies to generate in the output.
            (default: hpge, source, and lead_castle)"""
        ),
    )
    geom_opts.add_argument(
        "--hpge-name",
        action="store",
        required=True,
        help="""Name of the detector eg "V07302A".""",
    )
    geom_opts.add_argument(
        "--campaign",
        action="store",
        default="c1",
        help="""Name of the campaign eg "c1".""",
    )
    geom_opts.add_argument(
        "--measurement",
        action="store",
        required=True,
        help="""Name of the measurement eg "am_HS1_top_dlt".""",
    )

    source_opts = geom_opts.add_mutually_exclusive_group(required=False)
    source_opts.add_argument(
        "--run",
        action="store",
        type=int,
        help="""Number of the run eg 1.""",
    )
    source_opts.add_argument(
        "--source_position",
        nargs=3,
        type=float,
        action="store",
        metavar=("phi", "r", "z"),
        help="""Source position in phi, r, z  eg "0.0, 45.0, 3.0".""",
    )

    parser.add_argument(
        "filename",
        default=None,
        nargs="?",
        help="""File name for the output GDML geometry.""",
    )

    args = parser.parse_args(argv)

    if "source" in args.assemblies and args.run is None and args.source_position is None:
        parser.error(
            "When 'source' assembly is requested, you must specify either --run or --source_position."
        )

    if not args.visualize and args.filename == "":
        parser.error("no output file and no visualization specified")

    return args
