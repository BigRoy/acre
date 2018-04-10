import os
import pprint

from . import get_tools, compute, merge, which, launch


def launch(tools, executable, args):

    tools_env = get_tools(tools.split(";"))
    env = compute(tools_env)

    env = merge(env, current_env=dict(os.environ))
    print("Environment:\n%s" % pprint.pformat(env, indent=4))

    # Search for the executable within the tool's environment
    # by temporarily taking on its `PATH` settings
    exe = which(executable, env)
    if not exe:
        raise ValueError("Unable to find executable: %s" % executable)

    print("Launching: %s" % exe)
    launch(exe, environment=env, args=args)


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

    launch(tools=kwargs.tools, executable=kwargs.executable, args=args)
