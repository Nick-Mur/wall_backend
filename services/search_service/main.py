import uvicorn
from libs.fastapi.app_factory import create_app
from services.search_service.api.router import router as search_router
from libs.config_loader import load_config

config = load_config("services/search_service/config.json", env_prefix="SEARCH_SERVICE")

app = create_app(
    title="search_service",
    routers=[search_router]
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)