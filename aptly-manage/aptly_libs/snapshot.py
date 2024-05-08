import fnmatch
import datetime as dt
from . import supporting as sp


def snapshot_drop(mirror_settings, parameters):
    existing_snapshots = sp.get_existing_items("snapshot")
    calculated_snapshots = sp.generate_names(mirror_settings, parameters)
    for snapshot in calculated_snapshots:
        filter = f"{snapshot}"
        if parameters["date"]:
            filter += f"-{parameters['date']}"
        if parameters["tag"] and parameters["date"]:
            filter += f"-{parameters['tag']}"
        elif parameters["tag"]:
            filter += f"-????-??-??-{parameters['tag']}"
        targets = fnmatch.filter(existing_snapshots, filter)
        for target in targets:
            if not parameters["quiet"]:
                sp.display(f"Deleting snapshot {target}", parameters)
                cmd = f"aptly snapshot drop {target}"
                sp.run_raw_command(cmd, parameters)


def snapshot_list(mirror_settings, parameters):
    existing_snapshots = sp.get_existing_items("snapshot")
    calculated_snapshots = sp.generate_names(mirror_settings, parameters)
    found = []
    for snapshot in calculated_snapshots:
        if parameters["date"]:
            filter = f"{snapshot}-{parameters['date']}"
        else:
            filter = f"{snapshot}-[0-9]*"
        result = fnmatch.filter(existing_snapshots, filter)
        for res in result:
            found.append(res)
    for x in set(found):
        print(f"Snapshot found: {x}")


def snapshot_create(mirror_settings, parameters):
    existing_mirrors = sp.get_existing_items("mirror")
    existing_locals = sp.get_existing_items("repo")
    existing_mirrors.extend(existing_locals)
    names = sp.generate_names(mirror_settings, parameters)
    date = dt.datetime.now()
    existing_snapshots = sp.get_existing_items("snapshot")
    tag = parameters["tag"]
    for mirror in names:
        if mirror in existing_mirrors:
            name = f"{mirror}-{date.strftime('%Y-%m-%d')}-{tag}"
            if mirror in existing_locals:
                command = "repo"
            else:
                command = "mirror"
            cmd = f"aptly snapshot create {name} from {command} {mirror}"
            if name not in existing_snapshots:
                sp.display(f"Creating snapshot {name}", parameters)
                sp.run_raw_command(cmd, parameters)
            else:
                sp.display(f"Snapshot {name} already exists... not creating.", parameters)
        else:
            print(f"Mirror: {mirror} does not exist but was in scope for snapshotting!")
