import uvicorn

from libs.config_loader import load_config
from libs.fastapi.app_factory import create_app
from libs.postgres.schema import init_db_schema
from services.message_service.api.router import router as message_router

config = load_config("services/message_service/config.json", env_prefix="MESSAGE_SERVICE")

app = create_app(
    title="The Wall",
    routers=[message_router],
)
app.add_event_handler("startup", init_db_schema)


if __name__ == "__main__":
    server_config = config.get("server", {})
    uvicorn.run(
        app,
        host=server_config.get("host", "0.0.0.0"),
        port=int(server_config.get("port", 8002)),
    )
