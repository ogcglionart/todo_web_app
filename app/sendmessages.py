import requests

def send_to_telegram(message):
    bot_token = "8242022243:AAE5hYZFRtTHPnAgBekxAIOzWH9RvM3J9Ec"
    chat_id = "7337023780"
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    requests.post(url, data={"chat_id": chat_id, "text": message})
