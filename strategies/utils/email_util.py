import requests

from .system_configs import email_config


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