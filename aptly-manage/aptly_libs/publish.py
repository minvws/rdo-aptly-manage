import itertools
import sys
from . import supporting as sp


def generate_publish_endpoint(distro, distribution, parameters, suite):
    if suite and suite != "main":
        temp_endpoint = f"{distro}-{suite}-{parameters['target']} {distribution}"
    else:
        temp_endpoint = f"{distro}-{parameters['target']} {distribution}"
    endpoint = temp_endpoint.replace("/", "-").replace("_", "-")
    return endpoint


def publish_drop(mirror_settings, parameters):
    # aptly publish drop bookworm debian-updates
    # aptly publish drop distribution distro-suite
    existing_endpoints = sp.get_existing_items("publish")
    for distro in mirror_settings.keys():
        if mirror_settings[distro]["type"] == "distro":
            combinations = list(
                itertools.product(
                    [distro],
                    mirror_settings[distro]["distributions"],
                    mirror_settings[distro]["suites"],
                )
            )
        else:
            combinations = list(
                itertools.product(
                    [distro],
                    mirror_settings[distro]["distributions"],
                )
            )
        for combo in combinations:
            if mirror_settings[distro]["type"] == "distro":
                distro, distribution, suite = combo[0], combo[1], combo[2]
            else:
                distro, distribution, suite = combo[0], combo[1], None
            endpoint = generate_publish_endpoint(distro, distribution, parameters, suite)
            name = f"{endpoint.split()[1]} {endpoint.split()[0]}"
            filtername = f"{endpoint}"
            if filtername in existing_endpoints:
                cmd = f"aptly publish drop {name}"
                sp.display(f"Dropping published endpoint {name}", parameters)
                sp.run_raw_command(cmd, parameters)
            else:
                sp.display(f"No published endpoint found for {name}", parameters)


def publish_snapshot(mirror_settings, parameters):
    existing_endpoints = sp.get_existing_items("publish")
    # [print(x) for x in existing_endpoints]
    for distro in parameters["distros"]:
        settings = {distro: mirror_settings[distro]}
        # print(settings)
        for distribution in settings[distro]["distributions"]:
            custom_params = {k: v for k, v in parameters.items()}
            if settings[distro]["type"] == "distro":
                for suite in mirror_settings[distro]["suites"]:
                    endpoint = generate_publish_endpoint(distro, distribution, parameters, suite)
                    if endpoint in existing_endpoints and parameters["action"] != "switch":
                        print(f"Published endpoint exists: {endpoint}")
                        continue
                    custom_params.update(
                        {
                            "distros": distro,
                            "distributions": distribution,
                            "components": settings[distro]["components"],
                            "suites": suite,
                            "date": parameters["date"],
                            "tag": parameters["tag"],
                            "target": parameters["target"],
                        }
                    )
                    # print(custom_params)
                    generate_published_snapshot(settings, custom_params, distro, distribution, suite)
            else:
                if "mirrorfix" in settings[distro].keys():
                    if not parameters["action"] == "switch":  # hack for colabonline
                        distribution = ""
                custom_params.update(
                    {
                        "distros": distro,
                        "distributions": distribution,
                        "components": settings[distro]["components"],
                        "date": parameters["date"],
                        "tag": parameters["tag"],
                        "target": parameters["target"],
                    }
                )
                generate_published_snapshot(settings, custom_params, distro, distribution)


def generate_published_snapshot(settings, parameters, distro, distribution, suite=None):
    sanitized_settings = sp.sanitize_repo(settings, parameters)
    names = sp.generate_names(sanitized_settings, parameters)
    snapshot_names = []
    if names:
        for name in names:
            snapshot_names.append(f"{name}-{parameters['date']}-{parameters['tag']}")
    else:
        snapshot_names.append(f"{distro}-{parameters['date']}-{parameters['tag']}")  # fix for colabonline repo
    endpoint = generate_publish_endpoint(distro, distribution, parameters, suite)

    basecmd = f"""aptly publish {parameters['action']} -batch=true -passphrase-file=/etc/aptly-manage/passphrase.txt -component={','.join(settings[distro]['components'])}"""  # noqa: E501
    if parameters["action"] == "snapshot":
        cmd = f"{basecmd} -distribution={distribution} {' '.join(snapshot_names)} {endpoint.split()[0]}"
    elif parameters["action"] == "switch":
        cmd = f"{basecmd} {endpoint.split()[1]} {endpoint.split()[0]} {' '.join(snapshot_names)}"
    else:
        print(f"Wrong publish action: {parameters['action']}")
        sys.exit(1)
    if not parameters["quiet"]:
        print(f"{parameters['action']} endpoint {endpoint}")
    sp.run_raw_command(cmd, parameters)
