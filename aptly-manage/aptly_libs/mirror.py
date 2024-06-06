import sys
from . import supporting as sp


def mirror_list(mirror_settings, parameters=None):
    existing_mirrors = sp.get_existing_items("mirror")
    for mirror in existing_mirrors:
        print(f"Mirror: {mirror}")


def mirror_create(mirror_settings, parameters=None):
    """
    A mirror for each distribution suite component combination is created
    There is quite a bit of Debian/Ubuntu specific logic applied to generate the correct string
    """
    existing_mirrors = sp.get_existing_items("mirror")
    combinations = sp.generate_combos(mirror_settings, parameters)
    resultlist = []
    for item in combinations:
        resultlist.append(item)
        basecmd = generate_mirror_command(item)
        name = sp.generate_name(item)
        cmd = None
        if item["type"] == "local":
            sp.display(f"{name} is a local repo (not creating mirror)...", parameters)
            continue
        if name not in existing_mirrors:
            cmd = f"{name} {item['mirror']}"
            if item["appendix"]:
                cmd += f"/{item['appendix']}/"
            if item["type"] == "distro":
                if item["suite"] == "main":
                    cmd += f" {item['distribution']} {item['component']}"
                else:
                    if item["suite"] == "security" and item["distro"] == "debian":  # specific for Debian
                        cmd += f" {item['distribution']}-{item['suite']}/updates {item['component']}"
                    else:
                        cmd += f" {item['distribution']}-{item['suite']} {item['component']}"
            elif item["type"] == "repo":
                cmd += f" {item['distribution']}"
                if "component" in item.keys():
                    if item["component"] != "main":
                        cmd += f" {item['component']}"
            basecmd.extend(cmd.split())
            sp.display(f"Creating mirror {name}", parameters)
            sp.run_raw_command(basecmd, parameters, raw=True)
        else:
            sp.display(f"Mirror: {name} already exists", parameters)


def mirror_update(mirror_settings, parameters):
    existing_mirrors = sp.get_existing_items("mirror")  # aptly mirror list
    existing_locals = sp.get_existing_items("repo")
    names = sp.generate_names(mirror_settings, parameters)
    for mirror in names:
        if mirror in existing_locals:
            print(f"Not updating local repo {mirror}")
            continue
        if mirror in existing_mirrors:
            sp.display(f"Updating mirror: {mirror}", parameters)
            if mirror == "zammad_ubuntu-20.04-main":
                cmd = f"aptly mirror update -ignore-checksums {mirror}"
            else:
                cmd = f"aptly mirror update {mirror}"
            output = sp.run_raw_command(cmd, parameters)
            if output:
                if output.returncode != 0:
                    print(f"Error: failed to update mirror {mirror}")
                    sys.exit(1)
        else:
            print(f"Not updating: {mirror} - does not exist")


def mirror_drop(mirror_settings, parameters):
    existing_mirrors = sp.get_existing_items("mirror")
    names = sp.generate_names(mirror_settings, parameters)
    for name in names:
        if name in existing_mirrors:
            sp.display(f"Dropping mirror {name}", parameters)
            cmd = f"aptly mirror drop {name}"
            sp.run_raw_command(cmd, parameters)


def generate_mirror_command(mirror):
    cmd = ["aptly", "mirror", "create", "-architectures=amd64"]
    # print(mirror)
    if mirror["type"] == "distro":
        cmd.extend(["-with-udebs", "-with-installer"])
    else:  # must be repo
        appendstring = None
        if mirror["packages"]:
            packages = ",".join(mirror["packages"])
            cmd.append("-filter-with-deps")
            if mirror["versions"]:
                appendstring = f"-filter={packages}, $Version ({mirror['versions']})"
            else:
                appendstring = f"-filter={packages}"
        if appendstring:
            cmd.append(appendstring)
    return cmd
