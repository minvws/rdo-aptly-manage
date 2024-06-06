import subprocess
import sys
import itertools


def display(message, parameters):
    if not parameters["quiet"]:
        print(f"{message}")


def run_raw_command(command, parameters, raw=False):
    if not raw:
        command = command.split()
    if parameters["dry_run"]:
        print(f"{' '.join(command)} | DRY RUN")
        return False
    else:
        try:
            result = subprocess.run(command, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            if result.returncode > 0:
                stdout = result.stdout.decode("UTF-8").strip()
                stderr = result.stderr.decode("UTF-8").strip()
                print(f"\nAn error occurred: stderr: {stderr} - stdout: {stdout} - returncode: {result.returncode} \n")
        except KeyboardInterrupt:
            print("\n ctrl-c pressed - Aborted by user....\n")
            sys.exit(1)
    return result


def get_existing_items(command):
    cmd = f"aptly {command} list --raw"
    override = {"dry_run": False}
    items = run_raw_command(cmd, override)
    return items.stdout.decode("UTF-8").splitlines()


def generate_name(repodict):
    # print(repodict)
    if "mirrorfix" in repodict.keys():
        distribution = ""
    else:
        distribution = f"-{repodict['distribution']}"

    if repodict["type"] == "local":
        result = f"{repodict['distro']}"
    elif repodict["type"] == "distro":
        if repodict["suite"] == "main":
            result = f"{repodict['distribution']}-{repodict['component']}"
        else:
            result = f"{repodict['distribution']}-{repodict['component']}-{repodict['suite']}"
    else:
        if repodict["suite"]:
            if repodict["suite"] == "main":
                result = f"{repodict['distro']}{distribution}"
            else:
                result = f"{repodict['distro']}{distribution}-{repodict['suite']}"
        else:
            if "component" in repodict.keys():
                result = f"{repodict['distro']}{distribution}-{repodict['component']}"
            else:
                result = f"{repodict['distro']}{distribution}"
    return result


def generate_names(mirror_settings, parameters):
    combinations = generate_combos(mirror_settings, parameters)
    names = list(map(generate_name, combinations))
    return set(names)


def create_combo_dict(settings, distro, distribution, component, suite, parameters):
    """At first, creating combinations should be very simple. However distros have their own
    logic regarding how upstream repos are formatted, this is why this funciton is so long.
    """
    returndict = {"distro": distro, "distribution": distribution}
    # if filter_combo_dict(settings, distro, distribution, component, suite, parameters):
    if settings["type"] == "distro":
        if suite == "main":
            returndict["suite"] = "main"
            returndict["appendix"] = distro
        else:
            returndict["suite"] = suite
            returndict["appendix"] = settings["mirror_appendix"][suite]
    elif settings["type"] == "repo" or settings["type"] == "local":
        returndict["appendix"] = settings["mirror_appendix"]
        if suite:
            if suite == "main":
                returndict["suite"] = "main"
            else:
                returndict["suite"] = suite
        else:
            returndict["suite"] = None
        returndict["packages"] = settings["packages"]
        returndict["versions"] = settings["versions"]
        if "mirrorfix" in settings.keys():
            returndict["mirrorfix"] = settings["mirrorfix"]
    else:
        # print(f"Distro type {mirror_settings[distro]['type']} unknown")
        sys.exit(1)
    if component:  # only for colabonline repo!!
        returndict["component"] = component
    returndict["type"] = settings["type"]
    if distro == "ubuntu" and suite == "security":  # Ubuntu has separate security mirror
        returndict["mirror"] = settings["mirror_security"]
    else:
        returndict["mirror"] = settings["mirror"]
    return returndict


def filter_value(key, value, parameters):
    valid = False
    if value in parameters[key]:
        valid = True
    return valid


def sanitize_repo(mirror_settings, parameters):
    """Parameter input is used to filter the data first"""
    sanitized = {}
    for distro, settings in mirror_settings.items():
        temp_dict = {distro: {}}
        if distro in parameters["distros"]:
            for k, v in settings.items():
                if k in parameters.keys():
                    whitelisted_elements = list(filter(lambda e: filter_value(k, e, parameters), v))
                    temp_dict[distro].update({k: whitelisted_elements})
                else:
                    temp_dict[distro].update({k: v})
            sanitized.update(temp_dict)
    return sanitized


def generate_combos(mirror_settings, parameters):
    combinations = []
    for distro, settings in mirror_settings.items():
        if settings["type"] == "distro":
            product = itertools.product(settings["distributions"], settings["suites"], settings["components"])
            for element in product:
                result = create_combo_dict(settings, distro, element[0], element[2], element[1], parameters)
                combinations.append(result)
        elif settings["type"] == "repo" or settings["type"] == "local":
            if settings["components"]:
                product = itertools.product(settings["distributions"], settings["components"])
                for element in product:
                    result = create_combo_dict(settings, distro, element[0], element[1], None, parameters)
                    combinations.append(result)
            else:
                for element in settings["distributions"]:
                    result = create_combo_dict(settings, distro, element, None, None, parameters)
                    combinations.append(result)
        else:
            print("This is probably a bug")
            sys.exit(1)
    return combinations
