import requests


url = 'https://api.sendgrid.com/v3/mail/send'


headers = {
    'Authorization': 'Bearer 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',
    'Content-Type': 'application/json'
}


data = {
    "personalizations": [
        {
            "to": [
                {
                    "email": "alex_rozhkov@ukr.net"
                }
            ]
        }
    ],
    "from": {
        "email": "noreply@truckdispatch.pro"
    },
    "subject": "Sending with SendGrid is Fun",
    "content": [
        {
            "type": "text/plain",
            "value": "and easy to do anywhere, even with cURL"
        }
    ]
}

response = requests.post(url, headers=headers, data=data)

print(response.status_code)



'''
import os

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


message = Mail(
    from_email='noreply@truckdispatch.pro',
    to_emails='alexrothebest228@gmail.com',
    subject='Sending with Twilio SendGrid is Fun',
    html_content='7'
)


sg = SendGridAPIClient('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')
response = sg.send(message)
print(response.status_code)
print(response.body)
print(response.headers)
'''