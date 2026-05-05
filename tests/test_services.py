import unittest
from tempfile import TemporaryDirectory
from pathlib import Path

from app.config import loadSettings, validateHostConfig
from app.remote import buildSshCommand
from app.services import (
    getAllowedActions,
    getAllowedServices,
    getServiceUnit,
    validateAction,
    validateService,
)


class ServiceTests(unittest.TestCase):
    def test_configured_services_are_loaded(self):
        services = getAllowedServices()

        self.assertIn("gallinerito", services)
        self.assertEqual("gallinerito.service", services["gallinerito"])

    def test_service_key_is_translated_to_systemd_unit(self):
        self.assertEqual("ssh.service", getServiceUnit("ssh"))

    def test_unknown_service_is_rejected(self):
        with self.assertRaises(ValueError):
            getServiceUnit("unknown")

    def test_unknown_systemd_unit_is_rejected(self):
        with self.assertRaises(ValueError):
            validateService("unknown.service")

    def test_actions_are_restricted(self):
        self.assertIn("is-active", getAllowedActions())

        with self.assertRaises(ValueError):
            validateAction("disable")

    def test_empty_action_is_rejected(self):
        with self.assertRaises(ValueError):
            validateAction("")

    def test_systemd_unit_names_are_restricted(self):
        validateService("ssh.service")

        with self.assertRaises(ValueError):
            validateService("mysql.service")

    def test_missing_settings_file_shows_clear_error(self):
        with TemporaryDirectory() as directory:
            missingPath = Path(directory) / "settings.json"

            with self.assertRaisesRegex(ValueError, "No se encontro"):
                loadSettings(missingPath)

    def test_invalid_settings_json_shows_clear_error(self):
        with TemporaryDirectory() as directory:
            settingsPath = Path(directory) / "settings.json"
            settingsPath.write_text("{invalid json", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "JSON valido"):
                loadSettings(settingsPath)

    def test_valid_host_config_accepts_optional_port_and_key(self):
        hostData = {
            "user": "pablo",
            "host": "192.168.1.50",
            "port": 2222,
            "key_path": "~/.ssh/id_rsa",
        }

        validateHostConfig("raspberry", hostData)

    def test_host_config_requires_user_and_host(self):
        with self.assertRaisesRegex(ValueError, "usuario"):
            validateHostConfig("raspberry", {"host": "192.168.1.50"})

        with self.assertRaisesRegex(ValueError, "direccion"):
            validateHostConfig("raspberry", {"user": "pablo"})

    def test_host_config_rejects_invalid_port(self):
        hostData = {"user": "pablo", "host": "192.168.1.50", "port": "22"}

        with self.assertRaisesRegex(ValueError, "puerto"):
            validateHostConfig("raspberry", hostData)

    def test_ssh_command_uses_port_and_key_path(self):
        hostData = {
            "user": "pablo",
            "host": "192.168.1.50",
            "port": 2222,
            "key_path": "~/.ssh/id_rsa",
        }

        command = buildSshCommand(hostData, ["systemctl", "status", "ssh.service"])

        self.assertIn("-p", command)
        self.assertIn("2222", command)
        self.assertIn("-i", command)
        self.assertIn("~/.ssh/id_rsa", command)
        self.assertIn("pablo@192.168.1.50", command)


if __name__ == "__main__":
    unittest.main()
