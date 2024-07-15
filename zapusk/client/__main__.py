from type_docopt import docopt
import importlib.metadata

from zapusk.client.command_manager import CommandManager
from zapusk.models.job import JOB_STATE_ENUM


doc = """zapusk-client


Usage:
  zapusk-client -h | --help
  zapusk-client --version
  zapusk-client run <job_config_id> [--colors|--no-colors] [--tail]
  zapusk-client exec <command> [--name=<name>] [--group=<group>] [--tail] [--schedule=<cron_expression>] [--colors|--no-colors]
  zapusk-client cancel <job_id> [--scheduled] [--colors|--no-colors]
  zapusk-client tail <job_id>
  zapusk-client list [--filter=<state>|--scheduled] [--colors|--no-colors]
  zapusk-client config_jobs [--colors|--no-colors]
  zapusk-client config_groups [--colors|--no-colors]
  zapusk-client waybar


Options:
  -h --help                     Show this screen
  --version                     Show version.
  --colors                      Enable colors 
  --no-colors                   Disable colors 
  --filter=<state>              Filter running jobs by status [type: JobState]
  -n --name=<name>              Name for a command
  -g --group=<group>            Job group to run command in
  -t --tail                     Tail logfile immediately

Examples:
    zapusk run upload_to_s3
    zapusk status
"""

version = importlib.metadata.version("zapusk")


class JobState:
    STATES = [e.value for e in JOB_STATE_ENUM]

    def __init__(self, state):
        try:
            assert state in self.STATES
            self.state = state
        except AssertionError as e:
            print(
                f"Status filter has wrong value. Possible values are {', '.join(self.STATES)}",
            )
            exit(1)


def main():
    args = docopt(doc, version=version, types={"JobStatus": JobState})

    colors = None

    if args["--colors"] == True:
        colors = True

    if args["--no-colors"] == True:
        colors = False

    command_manager = CommandManager(colors=colors)

    if args["run"] == True:
        command_manager.run.run(
            job_config_id=str(args["<job_config_id>"]),
        )
        return

    if args["exec"] == True:
        command_manager.exec.run(
            command=str(args["<command>"]),
            group_id=str(args["--group"]) if args["--group"] else None,
            name=str(args["--name"]) if args["--name"] else None,
            schedule=str(args["--schedule"]) if args["--schedule"] else None,
            tail=bool(args["--tail"]),
        )
        return

    if args["cancel"] == True:
        command_manager.cancel.run(
            job_id=str(args["<job_id>"]),
            scheduled=bool(args["--scheduled"]),
        )
        return

    if args["list"] == True:
        command_manager.list.run(
            scheduled=bool(args["--scheduled"]),
            filter=args["--filter"].state if args["--filter"] else None,
        )
        return

    if args["list"] == True:
        command_manager.list.run(
            scheduled=bool(args["--scheduled"]),
            filter=args["--filter"],
        )
        return

    if args["config_groups"] == True:
        command_manager.config_groups.run()
        return

    if args["config_jobs"] == True:
        command_manager.config_jobs.run()
        return

    if args["waybar"] == True:
        command_manager.waybar.run()
        return

    if args["tail"] == True:
        command_manager.tail.run(
            job_id=str(args["<job_id>"]),
        )
        return

    command_manager.output.json({"error": "Command not found"})


if __name__ == "__main__":
    main()
