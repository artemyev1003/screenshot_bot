import os
import time
import requests
from dotenv import load_dotenv
from screenshot_tool import take_screenshot


# Value is loaded from the environment variable that is put into .env file
# and extracted using load_dotenv() function of python-dotenv module
load_dotenv()
TG_TOKEN = os.getenv('TG_TOKEN')
URL = f"https://api.telegram.org/bot{TG_TOKEN}/"


def check_tg_connection():
    """
    Checks connection to the Telegram API.
    """
    url = URL + 'getMe'
    result = requests.get(url).json()
    if result.get("ok") is False:
        raise RuntimeError("Failed to connect to the Telegram bot. "
              "Telegram API token is invalid or missing.")
    print("Connected")


def get_updates(offset: int = None):
    """
    Checks if someone has contacted the bot.

    getUpdates method of the Telegram API is used
    to receive incoming updates. It returns an Array of Update objects.

    Offset is an identifier of the first update to be returned.
    """
    url = URL + "getUpdates?timeout=100"
    if offset:
        url += f"&offset={offset}"
    # Sends a GET request to the URL and encodes the response as json
    result = requests.get(url).json()
    return result.get("result")


def send_message(text: str, chat_id: int):
    """
    Sends the text to the chat using sendMessage Telegram Bot API method.
    """
    url = URL + f"sendMessage?text={text}&chat_id={chat_id}"
    requests.get(url)


def send_screenshot(img_path: str, text: str, chat_id: int):
    """
    Sends the image and the text to the chat using sendDocument Telegram Bot API method.
    """
    files = {'document': open(img_path, 'rb')}
    url = URL + f"sendDocument?caption={text}&chat_id={chat_id}"
    requests.post(url, files=files)


def get_status_code(url: str) -> str:
    """
    Returns a status code of the request if URL is valid.
    Otherwise, asks to enter a valid URL or informs about connection failure
    """
    try:
        result = requests.get(url)
        return str(result.status_code) + ' ' + result.reason
    except requests.exceptions.MissingSchema:
        return f"Please enter a valid URL. Perhaps you meant https://{url}?"
    except requests.exceptions.RequestException as e:
        return "Failed to connect: " + str(e)


def main():
    """
    Main function of the program.
    Starts an infinite loop in which checks for updates every 2 seconds.
    Sends a screenshot with a status code, a status code or an error message
    back to the user.
    """
    check_tg_connection()
    update_id = get_updates()[-1].get("update_id")  # ID of the last message sent to the bot
    while True:
        time.sleep(2)
        messages = get_updates(update_id)  # Getting updates
        for message in messages:
            """
            If update_id is less than the message's update_id,
            a new message has been received 
            """
            if update_id < message["update_id"]:
                update_id = message["update_id"]
                # Check if there is text in the message
                if user_message := message.get("message", {}).get("text"):
                    text = get_status_code(user_message)
                    chat = message["message"]["chat"]["id"]
                    if text.startswith("200"):
                        img_path = take_screenshot(url=user_message)
                        send_screenshot(img_path, text, chat)
                    else:
                        send_message(text, chat)


if __name__ == '__main__':
    main()
