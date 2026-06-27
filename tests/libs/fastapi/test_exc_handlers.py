import unittest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Extra
from libs.fastapi.exception_handlers import handle_validation_error, handle_server_error


class TestErrorHandlers(unittest.TestCase):
    def setUp(self):
        self.app = FastAPI()
        self.app.add_exception_handler(RequestValidationError, handle_validation_error)
        self.app.add_exception_handler(Exception, handle_server_error)  # <-- ЭТО ГЛАВНОЕ

        class UserCreate(BaseModel):
            name: str
            age: int
            email: str

            class Config:
                extra = Extra.forbid

        @self.app.post("/users/")
        async def create_user(user: UserCreate):
            return {"message": f"{user.name} created"}

        @self.app.get("/error/")
        async def raise_error():
            raise ValueError("Error")

        @self.app.get("/db-error/")
        async def db_error():
            raise ConnectionError("Database connection failed")

        self.client = TestClient(self.app)

    def test_should_return_422_for_missing_field(self):
        """Should return 422 for missing required field"""
        # given
        data = {"name": "Sergey", "age": 100}

        # when
        response = self.client.post("/users/", json=data)

        # then
        self.assertEqual(response.status_code, 422)
        data = response.json()
        self.assertEqual(data["error"], "RequestValidationError")
        self.assertEqual(data["detail"][0]["loc"], ["body", "email"])

    def test_should_return_422_for_wrong_type(self):
        """Should return 422 for wrong field type"""
        # given
        data = {
            "name": "Sergey",
            "age": "not_number",
            "email": "test@example.com"
        }

        # when
        response = self.client.post("/users/", json=data)

        # then
        self.assertEqual(response.status_code, 422)
        data = response.json()
        self.assertEqual(data["error"], "RequestValidationError")
        self.assertEqual(data["detail"][0]["loc"], ["body", "age"])
        self.assertIn("integer", data["detail"][0]["msg"].lower())

    def test_should_return_422_for_extra_field(self):
        """Should return 422 for extra field"""
        # given
        data = {
            "name": "Anna",
            "age": 30,
            "email": "anna@example.com",
            "extra": "should_not_be_here"
        }

        # when
        response = self.client.post("/users/", json=data)

        # then
        self.assertEqual(response.status_code, 422)
        data = response.json()
        self.assertEqual(data["error"], "RequestValidationError")
        self.assertEqual(data["detail"][0]["loc"], ["body", "extra"])

    def test_should_return_200_for_valid_data(self):
        """Should return 200 for valid data"""
        # given
        data = {
            "name": "Sergey",
            "age": 25,
            "email": "sergey@example.com"
        }

        # when
        response = self.client.post("/users/", json=data)

        # then
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("created", data["message"])

    # ============ ТЕСТЫ НА СТРУКТУРУ ОТВЕТА ============

    def test_should_have_correct_error_response_structure(self):
        """Should have correct error response structure"""
        # given
        data = {"name": "John"}

        # when
        response = self.client.post("/users/", json=data)

        # then
        self.assertEqual(response.status_code, 422)
        data = response.json()
        self.assertIn("error", data)
        self.assertIn("detail", data)
        self.assertIsInstance(data["error"], str)
        self.assertIsInstance(data["detail"], list)

    def test_should_not_expose_validation_context(self):
        data = {"name": "Sergey", "age": "not_number", "email": "test@example.com"}

        response = self.client.post("/users/", json=data)

        self.assertEqual(response.status_code, 422)
        error = response.json()["detail"][0]
        self.assertNotIn("ctx", error)


if __name__ == "__main__":
    unittest.main()
