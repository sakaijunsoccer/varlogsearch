import logging

from configs import settings
from flaskr import create_app

if settings.debug:
    logging.basicConfig(level=logging.DEBUG, handlers=[logging.StreamHandler()])
else:
    logging.basicConfig(filename=settings.log_file, level=logging.INFO)


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=settings.port, debug=settings.debug)
