import mock
from mock import call

from configs import settings


@mock.patch(
    "app.controllers.api.v1.log_search.EventLogFileBuffer.find_event",
    return_value=(["event1", "event2", "event3"], False),
)
@mock.patch("os.path.exists", return_value=True)
@mock.patch("os.open", return_value=True)
def test_api_search_success(mock_open, mock_exist, mock_event, client):
    response = client.get("/api/v1/search?filename=example.log&limit=5&keywords=test")
    assert response.status_code == 200
    mock_event.assert_has_calls(
        [
            call(["test"], 5, timeout=settings.search_timeout),
        ]
    )
    assert mock_exist.called is True
    assert {"events": ["event1", "event2", "event3"]} == response.json


@mock.patch(
    "app.controllers.api.v1.log_search.EventLogFileBuffer.find_event",
    return_value=(["event1", "event2", "event3"], False),
)
@mock.patch("os.path.exists", return_value=True)
@mock.patch("os.open", return_value=True)
def test_api_search_without_limit_will_be_default_success(
    mock_open, mock_exist, mock_event, client
):
    response = client.get("/api/v1/search?filename=example.log&keywords=test")
    assert response.status_code == 200
    mock_event.assert_has_calls([call(["test"], 10, timeout=settings.search_timeout)])
    assert mock_exist.called is True
    assert {"events": ["event1", "event2", "event3"]} == response.json


def test_api_search_no_filename_failure(client):
    response = client.get("/api/v1/search?limit=5&keywords=test")
    assert response.status_code == 400
    assert {"errorMessage": "filename is required"} == response.json


def test_api_search_no_keywords_failure(client):
    response = client.get("/api/v1/search?filename=system.log&limit=5")
    assert response.status_code == 400
    assert {"errorMessage": "keywords is required"} == response.json
