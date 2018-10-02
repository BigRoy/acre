import os
import sys
import time

from . import discover, build, merge, locate, launch


if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--tools",
                        help="The tool environments to include. "
                             "These should be separated by `;`",
                        required=True)
    parser.add_argument("--executable",
                        help="The executable to run. ",
                        required=True)

    kwargs, args = parser.parse_known_args()

    # Build environment based on tools
    tools = kwargs.tools.split(";")
    tools_env = discover(kwargs.tools.split(";"))
    env = build(tools_env)
    env = merge(env, current_env=dict(os.environ))

    # Search for the executable within the tool's environment
    # by temporarily taking on its `PATH` settings
    exe = locate(kwargs.executable, env)
    try:
        if not exe:
            raise ValueError("Unable to find executable: %s" % kwargs.executable)
    except Exception as exc:
        print(exc)
        time.sleep(10)
        sys.exit(1)

    print("\n\nLaunching: %s" % exe)
    try:
        launch(exe, environment=env, args=args)
    except Exception as exc:
        # Ensure we can capture any exception and give the user (and us) time
        # to read it
        print(exc)
        time.sleep(10)
        sys.exit(1)
