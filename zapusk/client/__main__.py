from type_docopt import docopt
import importlib.metadata

from zapusk.client.command_manager import CommandManager
from zapusk.models.job import JOB_STATE_ENUM


doc = """zapusk


Usage:
  zapusk -h | --help
  zapusk --version
  zapusk run <job_config_id> [--colors|--no-colors] [--tail]
  zapusk exec <command> [--name=<name>] [--group=<group>] [--tail] [--schedule=<cron_expression>] [--colors|--no-colors]
  zapusk cancel <job_id> [--scheduled] [--colors|--no-colors]
  zapusk tail <job_id>
  zapusk list [--filter=<state>|--scheduled] [--colors|--no-colors]
  zapusk config_jobs [--colors|--no-colors]
  zapusk config_groups [--colors|--no-colors]
  zapusk waybar


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

    # Execute npm i in background
    zapusk exec "npm i"

    # Execute pytest and tail its log
    zapusk exec "pytest -v" -t

    # Schedule command to run every minute
    zapusk exec "pung -c4 google.com" --schedule "*/1 * * * *"

    # Run some job defined in ~/.config/zapusk/config.yaml
    zapusk run youtube_dl

    # Cancel some job with id
    zapusk cancel 42

    # See logs with id of a job
    zapusk tail 42
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
