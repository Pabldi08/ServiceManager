import unittest

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

    def test_actions_are_restricted(self):
        self.assertIn("is-active", getAllowedActions())

        with self.assertRaises(ValueError):
            validateAction("disable")

    def test_systemd_unit_names_are_restricted(self):
        validateService("ssh.service")

        with self.assertRaises(ValueError):
            validateService("mysql.service")


if __name__ == "__main__":
    unittest.main()
