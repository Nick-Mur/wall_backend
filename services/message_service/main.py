# TODO: Собрать FastAPI-приложение message-service и подключить router.
import uvicorn
from libs.fastapi.app_factory import create_app
from services.message_service.api.router import router as message_router
from libs.config_loader import load_config

config = load_config("services/message_service/config.json", env_prefix="MESSAGE_SERVICE")

app = create_app(
    title="The Wall",
    routers=[message_router]
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
