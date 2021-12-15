import requests
import json

from .system_configs import email_config
from .system_configs import serverchan_config
from .system_configs import notification_callback_urls

def send_email(title, text):
    files = {
        'from': (None, email_config["from"]),
        'to': (None, email_config["to"]),
        'subject': (None, title),
        'text': (None, text),
    }

    print(title, text)
    domain_name = email_config["mailgun_domain_name"]
    response = requests.post(f"https://api.mailgun.net/v3/{domain_name}/messages", files=files, auth=('api', email_config["maingun_api_token"]))
    print(response.content)  
    
    
def send_server_chan(title, text, send_key=None, retry=5):
    if serverchan_config["send_key"] == "":
        return 
    for i in range(retry):
        try:
            print(title, text)
            send_key = send_key or serverchan_config["send_key"]
            data = {
                "title" : title,
                "desp" : text,
            }
            url = f"https://sctapi.ftqq.com/{send_key}.send"
            response = requests.post(url, data=data)
            print(response.json()["message"])
            return
        except Exception as e:
            print(f"Retrying.... {i}")
            print(e)

    
def send_notification_callback(title, text):
    print(title, text)
    for url in notification_callback_urls:
        try:
            print(f"Sending notification callback: {url}")
            data = {
                "title" : title,
                "desp" : text,
            }
            response = requests.post(url, data=json.dumps(data))
            print(response.content)
        except Exception as e:
            print(f"Failed to call notification callback url: {url}")
            print(e)
            
def send_notification(title, text):
    send_notification_callback(title, text)
    send_server_chan(title, text)