from typing import Optional

from zapusk.client.api_client import ApiClientError

from .command import Command


class CommandExec(Command):
    def run(
        self,
        command: str,
        name: Optional[str] = None,
        group_id: Optional[str] = None,
        schedule: Optional[str] = None,
        tail: bool = False,
    ):
        try:
            # exec scheduled job
            if schedule:
                created_job = self.api_client.create_scheduled_job(
                    {
                        "command": command,
                        "group_id": group_id,
                        "name": name,
                        "schedule": schedule,
                    }
                )

                self.print_json(created_job)
                return

            # exec normal job
            created_job = self.api_client.create_job(
                {
                    "command": command,
                    "group_id": group_id,
                    "name": name,
                }
            )

            if tail:
                self.manager.tail.run(created_job["id"])
                return

            self.print_json(created_job)

        except ApiClientError as ex:
            self.print_error(ex)
