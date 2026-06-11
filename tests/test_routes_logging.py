import logging
import os
import sys
import unittest

import werkzeug

if not hasattr(werkzeug, "__version__"):
    werkzeug.__version__ = "3.0.0"


PROJECT_PACKAGE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "todo_project")
)

if PROJECT_PACKAGE_DIR not in sys.path:
    sys.path.insert(0, PROJECT_PACKAGE_DIR)

from todo_project import app, bcrypt, db
from todo_project.models import Task, User


class ListHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.messages = []

    def emit(self, record):
        self.messages.append(record.getMessage())


class RoutesLoggingTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config.update(
            TESTING=True,
            WTF_CSRF_ENABLED=False,
            SECRET_KEY="test-secret-key",
            SQLALCHEMY_DATABASE_URI="sqlite:///test_site.db",
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
        )

        cls.log_handler = ListHandler()
        cls.log_handler.setLevel(logging.INFO)
        app.logger.addHandler(cls.log_handler)
        app.logger.setLevel(logging.INFO)

        with app.app_context():
            db.drop_all()
            db.create_all()

            hashed_password = bcrypt.generate_password_hash("secret123").decode("utf-8")
            user = User(username="wesbonf", password=hashed_password)
            db.session.add(user)
            db.session.commit()

    @classmethod
    def tearDownClass(cls):
        app.logger.removeHandler(cls.log_handler)
        with app.app_context():
            db.session.remove()
            db.drop_all()

        if os.path.exists("test_site.db"):
            os.remove("test_site.db")

    def setUp(self):
        self.client = app.test_client()
        self.log_handler.messages.clear()

    def login(self, username="wesbonf", password="secret123"):
        return self.client.post(
            "/login",
            data={"username": username, "password": password},
            follow_redirects=False,
        )

    def test_login_logs_success_and_failure(self):
        failure_response = self.client.post(
            "/login",
            data={"username": "admin", "password": "wrong"},
            follow_redirects=False,
        )
        self.assertEqual(failure_response.status_code, 200)
        self.assertTrue(
            any(
                "LOGIN_FALHA usuario=admin" in message and "ip=" in message
                for message in self.log_handler.messages
            )
        )

        self.log_handler.messages.clear()
        success_response = self.login()
        self.assertEqual(success_response.status_code, 302)
        self.assertTrue(
            any(
                "LOGIN_SUCESSO usuario=wesbonf" in message and "ip=" in message
                for message in self.log_handler.messages
            )
        )

    def test_task_logout_and_delete_logs(self):
        login_response = self.login()
        self.assertEqual(login_response.status_code, 302)

        self.log_handler.messages.clear()
        create_response = self.client.post(
            "/add_task",
            data={"task_name": "Task one"},
            follow_redirects=False,
        )
        self.assertEqual(create_response.status_code, 302)
        self.assertTrue(
            any(
                "TAREFA_CRIADA usuario=wesbonf tarefa=Task one" in message
                for message in self.log_handler.messages
            )
        )

        with app.app_context():
            task = Task.query.filter_by(content="Task one").first()
            self.assertIsNotNone(task)
            task_id = task.id

        self.log_handler.messages.clear()
        delete_response = self.client.get(f"/all_tasks/{task_id}/delete_task")
        self.assertEqual(delete_response.status_code, 302)
        self.assertTrue(
            any(
                f"TAREFA_EXCLUIDA usuario=wesbonf tarefa_id={task_id}" in message
                for message in self.log_handler.messages
            )
        )

        self.log_handler.messages.clear()
        logout_response = self.client.get("/logout")
        self.assertEqual(logout_response.status_code, 302)
        self.assertTrue(
            any(
                "LOGOUT usuario=wesbonf" in message
                for message in self.log_handler.messages
            )
        )


if __name__ == "__main__":
    unittest.main()
