import os
import time
import requests
import logging
import urllib.parse
from dotenv import load_dotenv


# Value is loaded from the environment variable that is put into .env file
# and extracted using load_dotenv() function of python-dotenv module
load_dotenv()
SCREENSHOTMACHINE_API_KEY = os.getenv('SCREENSHOTMACHINE_API_KEY')


def get_datetime() -> str:
    """
    Returns current time in the YYY-MM-DD_HH:mm format.
    """
    timestr = time.strftime("%Y-%m-%d_%H:%M")
    return timestr


def construct_filename(url: str) -> str:
    """
    Constructs a relative path to the .jpg file using
    current date and time and the url.
    """

    filename = f"screenshots/{get_datetime()}_{url}.jpg"
    return filename


def take_screenshot(url: str) -> str:
    """
    Function based on the API provided by https://www.screenshotmachine.com website.
    If the webpage was successfully accessed,
    takes a screenshot and saves it to the local directory.
    Returns a relative path to the saved file.
    """
    base = f'https://api.screenshotmachine.com?key={SCREENSHOTMACHINE_API_KEY}&dimension=1024xfull&url='
    encoded_url = urllib.parse.quote_plus(url)
    response = requests.get(base + encoded_url)
    if response.status_code == 200:
        filename = construct_filename(encoded_url)

        if not os.path.exists("screenshots"):
            os.mkdir("screenshots")

        with open(filename, 'wb') as file:
            for chunk in response:
                file.write(chunk)
            logging.info(f"Screenshot saved as:\n {filename}")

        return filename
