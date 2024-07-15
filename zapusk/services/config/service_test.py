from unittest import TestCase

from testfixtures import Replacer, TempDirectory, replace_in_environ

from zapusk.services.config.constants import DEFAULT_COLORS
from .service import ConfigService


class TestConfigService(TestCase):
    def setUp(self) -> None:
        self.r = Replacer()
        self.r.in_environ("HOME", "/home/")

    def tearDown(self) -> None:
        self.r.restore()

    def test_config_service_should_return_jobs(self):
        config_service = ConfigService(config_path="./config.example.yaml")
        jobs = config_service.list_jobs()

        self.assertEqual(len(jobs), 3)
        self.assertEqual(
            jobs[0],
            {
                "name": "Sleep 10 Seconds",
                "id": "sleep_10",
                "group": "default",
                "command": "sleep 10",
                "cwd": "/var/",
                "args_command": None,
            },
        )

        self.assertEqual(
            jobs[1],
            {
                "name": "Sleep 30 Seconds",
                "id": "sleep_30",
                "group": "parallel",
                "command": "sleep 30",
                "cwd": "/home/",
                "args_command": None,
            },
        )

        self.assertEqual(
            jobs[2],
            {
                "name": "Configurable Sleep",
                "id": "sleep",
                "group": "sequential",
                "command": "sleep $1",
                "cwd": "/home/",
                "args_command": "zenity --entry --text 'Sleep Time'",
            },
        )

    def test_config_service_should_return_job_groups(self):
        config_service = ConfigService(config_path="./config.example.yaml")
        job_groups = config_service.list_jobgroups()

        self.assertEqual(len(job_groups), 3)
        self.assertEqual(
            job_groups[0],
            {
                "id": "default",
                "parallel": 10,
            },
        )

        self.assertEqual(
            job_groups[1],
            {
                "id": "sequential",
                "parallel": 1,
            },
        )

        self.assertEqual(
            job_groups[2],
            {
                "id": "parallel",
                "parallel": 2,
            },
        )

    def test_config_service_should_return_full_config(self):
        config_service = ConfigService(config_path="./config.example.yaml")
        config = config_service.get_config()

        self.assertEqual(len(config.job_groups), 3)
        self.assertEqual(len(config.jobs), 3)
        self.assertEqual(config.port, 9876)

    def test_config_service_should_return_job_group(self):
        config_service = ConfigService(config_path="./config.example.yaml")
        job_group = config_service.get_job_group("default")

        self.assertEqual(
            job_group,
            {
                "id": "default",
                "parallel": 10,
            },
        )

    def test_config_service_should_return_job_group_none(self):
        config_service = ConfigService(config_path="./config.example.yaml")
        job_group = config_service.get_job_group("unknown")

        self.assertEqual(job_group, None)

    def test_config_service_should_return_job_group_or_default(self):
        config_service = ConfigService(config_path="./config.example.yaml")
        job_group = config_service.get_job_group_or_default("unknown")

        self.assertEqual(
            job_group,
            {
                "id": "default",
                "parallel": 10,
            },
        )

    def test_config_service_should_return_job(self):
        config_service = ConfigService(config_path="./config.example.yaml")
        job = config_service.get_job("sleep_10")

        self.assertEqual(
            job,
            {
                "name": "Sleep 10 Seconds",
                "id": "sleep_10",
                "group": "default",
                "command": "sleep 10",
                "cwd": "/var/",
                "args_command": None,
            },
        )

    def test_config_service_should_return_job_none(self):
        config_service = ConfigService(config_path="./config.example.yaml")
        job = config_service.get_job("unknown")

        self.assertEqual(job, None)

    def test_config_path_1(self):
        with TempDirectory() as d:
            with replace_in_environ("APPDATA", d.path):
                d.makedir("zapusk")
                config_file = d / "zapusk/config.yml"
                config_file.write_text("")

                config_service = ConfigService()
                self.assertEqual(
                    config_service.config_path, f"{d.path}/zapusk/config.yml"
                )

    def test_config_path_2(self):
        with TempDirectory() as d:
            with replace_in_environ("XDG_CONFIG_HOME", d.path):
                d.makedir("zapusk")
                config_file = d / "zapusk/config.yaml"
                config_file.write_text("")

                config_service = ConfigService()
                self.assertEqual(
                    config_service.config_path, f"{d.path}/zapusk/config.yaml"
                )

    def test_config_path_3(self):
        with TempDirectory() as d:
            with replace_in_environ("HOME", d.path):
                with replace_in_environ("XDG_CONFIG_HOME", ""):
                    d.makedir(".config/zapusk")
                    config_file = d / ".config/zapusk/config.yaml"
                    config_file.write_text("")

                    config_service = ConfigService()
                    self.assertEqual(
                        config_service.config_path,
                        f"{d.path}/.config/zapusk/config.yaml",
                    )

    def test_config_path_fail(self):
        with TempDirectory() as d:
            with replace_in_environ("XDG_CONFIG_HOME", d.path):
                try:
                    ConfigService()
                except FileExistsError as ex:
                    self.assertEqual(ex.args[0], "Config not found")

    def test_config_should_contain_only_defaults_if_config_file_does_not_exist(self):
        config_service = ConfigService(
            config_path="/home/leonid_brezhnev/plenum/config.yaml"
        )
        config = config_service.get_config()

        self.assertEqual(len(config.job_groups), 1)
        self.assertEqual(
            config.job_groups["default"],
            {
                "id": "default",
                "parallel": 10,
                "on_finish": None,
                "on_fail": None,
            },
        )
        self.assertEqual(len(config.jobs), 0)
        self.assertEqual(config.port, 9876)
        self.assertEqual(config.colors, DEFAULT_COLORS)

        pass
