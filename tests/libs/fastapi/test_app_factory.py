import unittest
from fastapi.testclient import TestClient
from fastapi import FastAPI, APIRouter
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel

from libs.fastapi.app_factory import create_app
from libs.fastapi.exception_handlers import handle_server_error


class TestCreateApp(unittest.TestCase):

    def test_should_create_app_with_title(self):
        """Should create FastAPI app with title"""
        # given
        title = "My first app"

        # when
        app = create_app(title=title)

        # then
        self.assertIsInstance(app, FastAPI)
        self.assertEqual(app.title, title)

    def test_should_include_routers(self):
        """Should include routers"""
        # given
        router = APIRouter()

        @router.get("/test/")
        async def test_endpoint():
            return {"status": "ok"}

        # when
        app = create_app(title="App", routers=[router])
        client = TestClient(app)
        response = client.get("/test/")

        # then
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")

    def test_should_handle_multiple_routers(self):
        """Should handle multiple routers"""
        # given
        router1 = APIRouter(prefix="/v1")
        router2 = APIRouter(prefix="/v2")

        @router1.get("/test/")
        async def test1():
            return {"version": "v1"}

        @router2.get("/test/")
        async def test2():
            return {"version": "v2"}

        # when
        app = create_app(title="App", routers=[router1, router2])
        client = TestClient(app)

        # then
        response1 = client.get("/v1/test/")
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response1.json()["version"], "v1")

        response2 = client.get("/v2/test/")
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response2.json()["version"], "v2")

    def test_should_work_without_routers(self):
        """Should work without routers"""
        # given
        # when
        app = create_app(title="App")

        # then
        self.assertIsInstance(app, FastAPI)

        @app.get("/folder/")
        async def test():
            return {"folder": "secret"}

        client = TestClient(app)
        response = client.get("/folder/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["folder"], "secret")

    def test_should_register_validation_error_handler(self):
        """Should register validation error handler"""
        # given
        app = create_app(title="My first app")

        # ✅ ПРОВЕРЯЕМ, ЧТО ОБРАБОТЧИК ВАЛИДАЦИИ ЗАРЕГИСТРИРОВАН
        self.assertIn(RequestValidationError, app.exception_handlers)

        class UserCreate(BaseModel):
            name: str
            age: int

        @app.post("/users/")
        async def create_user(user: UserCreate):
            return {"name": user.name}

        client = TestClient(app)

        # when - отправляем запрос без обязательного поля age
        response = client.post("/users/", json={"name": "John"})

        # then
        self.assertEqual(response.status_code, 422)
        data = response.json()
        self.assertEqual(data["error"], "RequestValidationError")
        self.assertEqual(data["detail"][0]["loc"], ["body", "age"])


if __name__ == "__main__":
    unittest.main()
