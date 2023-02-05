import logging
import os.path

import flask
from flask import Blueprint, jsonify, request

from configs import settings
from app.models.event_log import EventLogFile, EventLogFileBuffer

DEFAULT_SEARCH_LOG_LINE = 10
PATH_VAR_LOGS = "/var/log"

api_v1 = Blueprint("v1", __name__, url_prefix="/api/v1")
logger = logging.getLogger(__name__)


@api_v1.route("/search", methods=["GET"])
def event_search() -> flask.Response:
    """Event data
    ---
    tags:
      - Event
    parameters:
      - name: filename
        in: query
        type: string
        required: true
      - name: keywords
        in: query
        example: "key1,key2"
        type: string
        required: true
      - name: limit
        in: query
        type: integer
        required: false
    produces:
      - application/json
    responses:
      200:
        description: Search data
        schema:
          items:
            $ref: '#/definitions/events'
    definitions:
      events:
        type: array
        items:
          type: string
    """
    filename = request.args.get("filename")
    if filename is None or filename == "":
        return jsonify({"errorMessage": "filename is required"}), 400
    keywords = request.args.get("keywords")
    if not keywords:
        return jsonify({"errorMessage": "keywords is required"}), 400
    keywords = keywords.split(",")
    limit_str = request.args.get("limit")
    limit = int(limit_str) if limit_str is not None else DEFAULT_SEARCH_LOG_LINE

    logger.info(
        {
            "action": "event_search",
            "filename": filename,
            "keywords": keywords,
            "limit": limit,
        }
    )

    full_filepath = os.path.join(PATH_VAR_LOGS, filename)
    if not os.path.exists(full_filepath):
        return jsonify({"errorMessage": "file does not exist"}), 404

    event_log_file = EventLogFileBuffer(full_filepath)
    match_line, is_timeout = event_log_file.find_event(keywords, limit, timeout=settings.search_timeout)
    logger.info(
        {
            "action": "event_search",
            "filename": filename,
            "keywords": keywords,
            "limit": limit,
            "lines": match_line,
            "timeout": is_timeout,
        }
    )

    json_search_result = {"events": match_line}
    if is_timeout:
        json_search_result['errorMessage'] = 'timeout'
        return jsonify(json_search_result), 400
    return jsonify(json_search_result)
