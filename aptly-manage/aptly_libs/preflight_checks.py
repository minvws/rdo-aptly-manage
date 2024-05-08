import sys


def preflight_check(parameters):
    if parameters["date"]:
        param_timestamp_len = len(parameters["date"])
        if param_timestamp_len > 0 and param_timestamp_len < 5:
            print(f"Parameter date has incorrect value: {parameters['date']}, forgot time/wildcard(*)?")
            sys.exit(1)

    if parameters["command"] == "snapshot":
        if parameters["action"] == "create" or parameters["action"] == "drop":
            if not parameters["tag"]:
                print("When creating or dropping a snapshot, you must spefify a --tag")
                sys.exit(1)

    if parameters["command"] == "mirror":
        if parameters["tag"] or parameters["date"]:
            print("Parameters --tag or --date not supported with command 'mirror'")
            sys.exit(1)

    if parameters["command"] == "publish":
        if parameters["action"] == "snapshot" or parameters["action"] == "switch":
            if not parameters["tag"] or not parameters["date"] or not parameters["target"]:
                print("Parameters --tag, --date and --target are required when publishing snapshots")
                sys.exit(1)

    if parameters["command"] == "publish" and parameters["action"] == "drop":
        if not parameters["target"]:
            print("Parameters --target required when dropping published snapshots (safety measure)")
            sys.exit(1)
