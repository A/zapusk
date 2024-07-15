import datetime
from itertools import islice
import json
import human_readable
import dateutil

from .api_client import ApiClientError
from .command import Command


STATE_LOOKUP = {
    "PENDING": " ",
    "RUNNING": " ",
    "FINISHED": " ",
    "FAILED": " ",
    "CANCELLED": " ",
}

TIME_PREFIX_LOOKUP = {
    "PENDING": "queued",
    "RUNNING": "started",
    "FINISHED": "finished",
    "FAILED": "failed",
    "CANCELLED": "cancelled",
}


class CommandWaybar(Command):
    def run(self):
        try:
            all_jobs = self.api_client.list_jobs()
            self.output.json(
                {
                    "text": self.__build_text(all_jobs),
                    "tooltip": self.__build_tooltip(all_jobs),
                },
                one_line=True,
            )

        except ApiClientError as ex:
            self.output.text("{" + f'"text": "{ex}"' + "}")

    def __build_text(self, all_jobs):
        pending_jobs = [i for i in all_jobs if i["state"] == "PENDING"]
        running_jobs = [i for i in all_jobs if i["state"] == "RUNNING"]
        finished_jobs = [i for i in all_jobs if i["state"] == "FINISHED"]
        failed_jobs = [i for i in all_jobs if i["state"] == "FAILED"]
        cancelled_jobs = [i for i in all_jobs if i["state"] == "CANCELLED"]

        return " ".join(
            [
                f"{STATE_LOOKUP['PENDING']} {len(pending_jobs)}",
                f"{STATE_LOOKUP['RUNNING']} {len(running_jobs)}",
                f"{STATE_LOOKUP['FINISHED']} {len(finished_jobs)}",
                f"{STATE_LOOKUP['FAILED']} {len(failed_jobs)}",
                f"{STATE_LOOKUP['CANCELLED']} {len(cancelled_jobs)}",
            ]
        )

    def __build_tooltip(self, all_jobs):
        LAST_JOBS_AMOUNT = 20
        now = datetime.datetime.now().timestamp()
        last_jobs = islice(reversed(all_jobs), LAST_JOBS_AMOUNT)

        return "\r\n".join(
            [
                f"<b>{i['name']}(id={i["id"]})</b> <i>{TIME_PREFIX_LOOKUP[i['state']]} {human_readable.date_time(now - self.__parse(i['updated_at']))}</i>"
                for i in last_jobs
            ]
        )

    def __parse(self, date_str):
        return dateutil.parser.parse(date_str, ignoretz=True).timestamp()  # type: ignore
