import argparse
import sys


def generate_options(mirror_settings):
    options = {
        "distributions": [],
        "components": [],
        "suites": [],
    }
    for k, v in mirror_settings.items():
        for kk, vv in v.items():
            if kk not in [
                "mirror_appendix",
                "mirror",
                "mirror_security",
                "type",
                "packages",
                "versions",
                "mirrorfix",
            ]:
                options[kk].extend(vv)

    for k, v in options.items():
        options[k] = set(v)

    options["distros"] = mirror_settings.keys()
    return options


def get_arguments(mirror_settings):
    options = generate_options(mirror_settings)
    parser = argparse.ArgumentParser(description="Manage Aptly Mirror & Snapshots")
    ag = parser.add_argument_group(title="Generic Settings")
    ag.add_argument(
        "-c",
        "--command",
        choices=["mirror", "snapshot", "publish"],
        help="Create mirrors for configured operating systems and versions",
        required=True,
    )
    ag.add_argument(
        "-a",
        "--action",
        choices=["list", "create", "drop", "update", "snapshot", "switch"],
        help="Specify command action, following aptly interface",
        required=True,
    )
    ag.add_argument(
        "--distros",
        type=str,
        nargs="+",
        choices=options["distros"],
        help="Limit action to particular Linux distro (Debian/Ubuntu)",
        default=options["distros"],
    )
    ag.add_argument(
        "--distributions",
        type=str,
        nargs="+",
        choices=options["distributions"],
        help="Limit action to particular Linux distro (Debian/Ubuntu)",
        default=options["distributions"],
    )
    ag.add_argument(
        "--components",
        type=str,
        nargs="+",
        choices=options["components"],
        help="Limit action to particular subgroup",
        default=options["components"],
    )
    ag.add_argument(
        "--suites",
        type=str,
        nargs="+",
        choices=options["suites"],
        help="Limit action to particular group",
        default=options["suites"],
    )
    ag.add_argument(
        "--target",
        choices=["tmp", "test", "stag", "prod"],
        help="Publish snapshots to tmp|test|stag|prod",
    )
    ag.add_argument("--tag", help="When creating snapshot, apply this tag")
    ag.add_argument(
        "--dry-run",
        action="store_true",
        help="Show the commands to be executed, but don't run them",
    )
    ag.add_argument(
        "-d",
        "--date",
        help="Specify timestamp as Y-m-d-HM: 2023-02-20-2310 as filter for snapshot selection/deletion",
    )
    ag.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="No output to console, usefull for running the script as part of automation",
    )
    ag.add_argument("-y", "--yes", action="store_true", help="Answer yes on all questions")
    # ag.add_argument( "--switch", help="Switch")
    return parser


def get_command_line_arguments(parser):
    try:
        args = parser.parse_args()
    except OSError:
        parser.print_help()
        sys.exit(1)

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    return args
