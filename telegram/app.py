from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Replace 'YOUR_TELEGRAM_BOT_TOKEN' with your Telegram bot token
TELEGRAM_BOT_TOKEN = '6663052612:AAEIe0LH1m88u6AhHhGT2AjSYd8Q-j-Osws'
# Replace 'YOUR_CHANNEL_NAME' with your Telegram channel name
TELEGRAM_CHANNEL_NAME = '@bot112020'

@app.route('/webhook', methods=['POST'])
def send_to_telegram():
    message = request.data.decode('utf-8')
    send_telegram_message(message)
    # Pass the message to the Web Page Service for display
    forward_to_web_page_service(message)
    return jsonify({'status': 'success'})

def send_telegram_message(message):
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    params = {
        'chat_id': TELEGRAM_CHANNEL_NAME,
        'text': message,
    }
    response = requests.post(telegram_url, params=params)
    print(response.json())

def forward_to_web_page_service(message):
    # URL of the Web Page Service
    WEB_PAGE_SERVICE_URL = 'http://20.198.10.178:8000/update_message'
    requests.post(WEB_PAGE_SERVICE_URL, data=message)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001, debug=True)
