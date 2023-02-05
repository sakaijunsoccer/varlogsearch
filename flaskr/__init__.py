from flasgger import Swagger
from flask import Flask

from app.controllers.api.v1 import log_search


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SWAGGER"] = {"title": "API"}
    app.register_blueprint(log_search.api_v1)

    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": "doc",
                "route": "/doc.json",
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/docs/api/v1/",
    }

    Swagger(app, config=swagger_config)
    return app
