import os
import urllib
import pytest
import unittest
import responses
import requests
import requests_mock
import json
from unittest import mock
from contextlib import ExitStack as does_not_raise
from parameterized import parameterized


import screenshot_tool
import bot
from screenshot_tool import construct_filename, take_screenshot
from bot import (
    check_tg_connection,
    get_updates,
    send_message,
    send_screenshot,
    get_status_code,
)


#  screenshot_tool module tests

@pytest.fixture(autouse=True)
def mock_get_datetime(monkeypatch):
    monkeypatch.setattr("screenshot_tool.get_datetime", lambda: "2023-01-01_00:01")


@pytest.fixture(autouse=True)
def mock_screenshotmachine_api_key(monkeypatch):
    monkeypatch.setattr("screenshot_tool.SCREENSHOTMACHINE_API_KEY", "111111")


def test_construct_filename():
    filename = construct_filename("https://br-analytics.ru")
    assert filename == "screenshots/2023-01-01_00:01_https://br-analytics.ru.jpg"


@responses.activate
@pytest.mark.parametrize("response_code, expected_result", [
    (200, True),
    (404, False)
])
def test_take_screenshot(response_code, expected_result):
    base = f'https://api.screenshotmachine.com?key=' \
           f'{screenshot_tool.SCREENSHOTMACHINE_API_KEY}&dimension=1024xfull&url='
    some_url = "https://www.some-url.com"
    encoded_url = urllib.parse.quote_plus(some_url)
    responses.add(method=responses.GET,
                  url=base+encoded_url,
                  status=response_code)
    take_screenshot("https://www.some-url.com")
    result = os.path.exists("screenshots/2023-01-01_00:01_https%3A%2F%2Fwww.some-url.com.jpg")
    assert result == expected_result


# bot module tests

@pytest.fixture(autouse=True)
def mock_tg_base_url(monkeypatch):
    monkeypatch.setattr("bot.URL", "https://api.telegram.org/bot_valid_token/")


response_json_fail = json.loads('{"ok":false,"error_code":"404","description":"Not Found"}')
response_json_success = json.loads('{"ok":true,"result":"successful result data"}')


@responses.activate
@pytest.mark.parametrize("tg_api_token, response_json, expectation", [
    ("valid_token", response_json_success, does_not_raise()),
    ("invalid_token", response_json_fail, pytest.raises(RuntimeError)),
    ("", response_json_fail, pytest.raises(RuntimeError))
])
def test_check_tg_connection(tg_api_token, response_json, expectation):
    url = f"https://api.telegram.org/bot{tg_api_token}/getMe"
    responses.add(method=responses.GET,
                  url=url,
                  json=response_json)

    bot.URL = f"https://api.telegram.org/bot{tg_api_token}/"

    with expectation:
        check_tg_connection()


url_wo_offset = "https://api.telegram.org/bot_valid_token/getUpdates?timeout=100"
url_with_offset = f"https://api.telegram.org/bot_valid_token/getUpdates?timeout=100&offset=55555"


@responses.activate
@pytest.mark.parametrize("offset, url", [
    (None, url_wo_offset),
    (55555, url_with_offset)
])
def test_get_updates(offset, url):
    responses.add(method=responses.GET,
                  url=url,
                  json=response_json_success)
    assert get_updates(offset) == "successful result data"


def test_send_message():
    send_message_url = "https://api.telegram.org/bot_valid_token/sendMessage?text=some_text&chat_id=333"
    with requests_mock.mock() as m:
        m.get(send_message_url)
        send_message("some_text", 333)
    assert m.called is True


def test_send_screenshot():
    send_screenshot_url = "https://api.telegram.org/bot_valid_token/sendDocument?caption=some_text&chat_id=333"
    with requests_mock.mock() as m:
        m.post(send_screenshot_url)
        mock_file = "screenshot.jpg"
        open(mock_file, 'a').close()
        send_screenshot(mock_file, "some_text", 333)
    assert m.called is True


@responses.activate
@pytest.mark.parametrize("message, response_code, expected_result", [
    ("https://www.existing-site.com", 200, "200 OK"),
    ("https://www.moved-site.com", 301, "301 Moved Permanently"),
    ("https://www.closed-site.com", 403, "403 Forbidden"),
    ("https://www.non-existing-site.com", 404, "404 Not Found"),
    ("https://www.malfunctioning-site.com", 500, "500 Internal Server Error"),
])
def test_get_status_code(message, response_code, expected_result):
    responses.add(method=responses.GET,
                  url=message,
                  status=response_code)
    result = get_status_code(message)
    assert result == expected_result


class TestGetStatusCodeFail(unittest.TestCase):
    @parameterized.expand([
        (requests.exceptions.RequestException, "Connection error"),
        (requests.exceptions.MissingSchema,
         "Please enter a valid URL. Perhaps you meant https://message?"
         )])
    def test_get_status_code_fail(self, exception, expected_result):
        with mock.patch("requests.get",
                        side_effect=exception()):
            result = get_status_code("message")
            assert result == expected_result
