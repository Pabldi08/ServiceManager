import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from app.hosts import parseHostInput
from app.storage import addHost, addHostServices, deleteHost, deleteHostService, loadData, makeServiceKey
from app.discovery import parseServiceUnits
from app.remote import buildSshCommand, makeCommandResult, validateRemoteCommand
from app.services import getServiceUnit, validateAction, validateService
from app.status import parseServiceState
from app.views import renderServiceList, renderServiceManagementDialog


class ServiceTests(unittest.TestCase):
    def test_host_input_is_parsed_with_default_port(self):
        hostData = parseHostInput("pablo@192.168.1.50")

        self.assertEqual("pablo", hostData["user"])
        self.assertEqual("192.168.1.50", hostData["host"])
        self.assertEqual(22, hostData["port"])
        self.assertEqual("pablo@192.168.1.50", hostData["name"])

    def test_host_input_is_parsed_with_custom_port(self):
        hostData = parseHostInput("pablo@192.168.1.50:2222")

        self.assertEqual(2222, hostData["port"])
        self.assertEqual("pablo@192.168.1.50:2222", hostData["name"])

    def test_invalid_host_input_is_rejected(self):
        with self.assertRaises(ValueError):
            parseHostInput("192.168.1.50")

        with self.assertRaises(ValueError):
            parseHostInput("pablo@192.168.1.50:ssh")

    def test_storage_creates_and_saves_hosts(self):
        with TemporaryDirectory() as directory:
            dataPath = Path(directory) / "service_manager.json"
            hostName = addHost(parseHostInput("pablo@192.168.1.50"), dataPath)
            data = loadData(dataPath)

            self.assertEqual("pablo@192.168.1.50", hostName)
            self.assertIn(hostName, data["hosts"])

    def test_selected_services_are_saved_per_host(self):
        with TemporaryDirectory() as directory:
            dataPath = Path(directory) / "service_manager.json"
            hostName = addHost(parseHostInput("pablo@192.168.1.50"), dataPath)

            added = addHostServices(
                hostName,
                ["ssh.service", "nginx.service", "not-valid.timer"],
                dataPath,
            )
            services = loadData(dataPath)["hosts"][hostName]["services"]

            self.assertEqual(["ssh.service", "nginx.service"], added)
            self.assertEqual("ssh.service", services["ssh"])
            self.assertEqual("nginx.service", services["nginx"])
            self.assertNotIn("not-valid", services)

    def test_hosts_and_services_can_be_deleted(self):
        with TemporaryDirectory() as directory:
            dataPath = Path(directory) / "service_manager.json"
            hostName = addHost(parseHostInput("pablo@192.168.1.50"), dataPath)
            addHostServices(hostName, ["ssh.service"], dataPath)

            deletedService = deleteHostService(hostName, "ssh", dataPath)
            self.assertEqual("ssh.service", deletedService)
            self.assertEqual({}, loadData(dataPath)["hosts"][hostName]["services"])

            deletedHost = deleteHost(hostName, dataPath)
            self.assertEqual(hostName, deletedHost)
            self.assertEqual({}, loadData(dataPath)["hosts"])

    def test_service_key_is_created_from_unit_name(self):
        self.assertEqual("ssh", makeServiceKey("ssh.service"))
        self.assertEqual("app_worker", makeServiceKey("app@worker.service"))

    def test_service_discovery_output_is_parsed(self):
        output = """
ssh.service loaded active running OpenBSD Secure Shell server
nginx.service loaded active running A high performance web server
not-a-service.timer loaded active waiting Timer
cloudflared.service loaded inactive dead cloudflared
ssh.service loaded active running OpenBSD Secure Shell server
"""

        services = parseServiceUnits(output)

        self.assertEqual(
            ["ssh.service", "nginx.service", "cloudflared.service"],
            services,
        )

    def test_host_specific_service_validation(self):
        data = {
            "hosts": {
                "raspberry": {
                    "user": "pablo",
                    "host": "192.168.1.50",
                    "port": 22,
                    "services": {"ssh": "ssh.service"},
                }
            }
        }

        with patch("app.config.loadData", return_value=data):
            self.assertEqual("ssh.service", getServiceUnit("ssh", "raspberry"))
            validateService("ssh.service", "raspberry")

            with self.assertRaises(ValueError):
                validateService("nginx.service", "raspberry")

    def test_actions_are_restricted(self):
        validateAction("is-active")

        with self.assertRaises(ValueError):
            validateAction("disable")

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

    def test_ssh_command_rejects_invalid_remote_command(self):
        hostData = {"user": "pablo", "host": "192.168.1.50", "port": 22}

        with self.assertRaises(ValueError):
            buildSshCommand(hostData, "systemctl status ssh.service")

        with self.assertRaises(ValueError):
            buildSshCommand(hostData, [])

        with self.assertRaises(ValueError):
            buildSshCommand(hostData, ["systemctl", ""])

    def test_remote_command_validation_accepts_argument_lists(self):
        validateRemoteCommand(["systemctl", "status", "ssh.service"])

    def test_command_result_has_consistent_shape(self):
        result = makeCommandResult(0, " output\n", " error\n")

        self.assertEqual(0, result["returncode"])
        self.assertEqual("output", result["stdout"])
        self.assertEqual("error", result["stderr"])

    def test_service_status_output_is_parsed(self):
        self.assertEqual("active", parseServiceState("active\n"))
        self.assertEqual("inactive", parseServiceState("inactive\n"))
        self.assertEqual("failed", parseServiceState("failed\n"))

    def test_unknown_service_status_is_reported(self):
        self.assertEqual("unknown", parseServiceState("unexpected\n"))
        self.assertEqual("unknown", parseServiceState(""))

    def test_service_list_renders_action_buttons_and_status_dots(self):
        services = {"ssh": "ssh.service", "nginx": "nginx.service"}
        actions = ["status", "is-active", "start", "stop", "restart"]
        statuses = [
            {"key": "ssh", "state": "active"},
            {"key": "nginx", "state": "inactive"},
        ]

        with patch("app.views.getAllowedServices", return_value=services):
            with patch("app.views.getAllowedActions", return_value=actions):
                html = renderServiceList("raspberry", statuses)

        for action in ["status", "start", "stop", "restart"]:
            self.assertIn(f'value="{action}"', html)

        self.assertNotIn('value="is-active"', html)
        self.assertIn("service-status-dot-active", html)
        self.assertIn("service-status-dot-inactive", html)
        self.assertEqual(len(services) * 4, html.count('name="action"'))

    def test_status_action_result_is_rendered_inside_selected_service(self):
        services = {"ssh": "ssh.service", "nginx": "nginx.service"}
        actions = ["status", "start", "stop", "restart"]
        selected = {"host": "raspberry", "service": "ssh", "action": "status"}
        result = {
            "returncode": 0,
            "stdout": "ssh.service is active",
            "stderr": "",
        }

        with patch("app.views.getAllowedServices", return_value=services):
            with patch("app.views.getAllowedActions", return_value=actions):
                html = renderServiceList("raspberry", selected=selected, result=result)

        self.assertIn("status-action-result", html)
        self.assertIn("Status result", html)
        self.assertIn("ssh.service is active", html)
        self.assertEqual(1, html.count("status-action-result"))

    def test_service_management_dialog_separates_included_and_available_services(self):
        services = {"ssh": "ssh.service"}
        discoveredServices = ["ssh.service", "nginx.service"]

        with patch("app.views.getAllowedServices", return_value=services):
            html = renderServiceManagementDialog("raspberry", discoveredServices)

        self.assertIn("Manage services", html)
        self.assertIn("Included", html)
        self.assertIn("Available to add", html)
        self.assertIn("Services found on raspberry.", html)
        self.assertIn("Add service nginx.service", html)
        self.assertIn("Remove service ssh", html)
        self.assertIn('class="shrink-0" method="post" action="/delete-service"', html)
        self.assertIn('class="shrink-0" method="post" action="/register-services"', html)
        self.assertIn("overflow-y-auto overflow-x-hidden", html)
        self.assertIn('action="/delete-service"', html)
        self.assertIn('action="/register-services"', html)
        self.assertIn("ssh.service", html)
        self.assertIn("nginx.service", html)


if __name__ == "__main__":
    unittest.main()
