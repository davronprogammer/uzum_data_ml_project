"""
Uzum Market Dashboard & Deployment Unit Test Suite
==================================================
Ushbu modul Dashboard fayli va Docker konfiguratsiyalarining to'g'riligini
avtomatlashtirilgan tarzda tekshiradi.
"""

import os
import unittest
import py_compile

class TestDashboardAndDeployment(unittest.TestCase):
    """Dashboard va Deployment tekshiruvlari."""

    def test_dashboard_syntax_validity(self):
        """1. app.py da sintaksis xatoliklari yo'qligini tekshirish."""
        app_path = "src/dashboard/app.py"
        self.assertTrue(os.path.exists(app_path), "app.py topilmadi!")
        # Sintaksis kompilyatsiyasi
        compiled = py_compile.compile(app_path)
        self.assertIsNotNone(compiled)

    def test_docker_configuration_files(self):
        """2. Dockerfile va docker-compose.yml mavjudligi va to'g'riligini tekshirish."""
        self.assertTrue(os.path.exists("Dockerfile"))
        self.assertTrue(os.path.exists("docker-compose.yml"))
        self.assertTrue(os.path.exists(".dockerignore"))

        with open("Dockerfile", "r", encoding="utf-8") as f:
            dockerfile_content = f.read()
            self.assertIn("EXPOSE 8501", dockerfile_content)
            self.assertIn("streamlit", dockerfile_content)

        with open("docker-compose.yml", "r", encoding="utf-8") as f:
            compose_content = f.read()
            self.assertIn("8501:8501", compose_content)

if __name__ == "__main__":
    unittest.main()
