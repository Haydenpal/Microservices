from flask import Flask, request, render_template, make_response
from io import BytesIO
from reportlab.pdfgen import canvas
from datetime import datetime

app = Flask(__name__)

# Global variables to store the latest messages
latest_alert_messages = []

# Webhook URL for receiving messages
WEBHOOK_URL = 'http://20.197.21.223:80/webhook'

@app.route('/')
def index():
    messages_with_info = []
    if latest_alert_messages:
       reversed_messages = reversed(latest_alert_messages)
       messages_with_info = [extract_info(message) for message in reversed_messages]
    return render_template('index.html', messages_with_info=messages_with_info)

@app.route('/update_message', methods=['POST'])
def update_message():
    global latest_alert_messages
    # Add the received message to the latest_alert_messages list
    latest_alert_messages.insert(0, request.data.decode('utf-8').strip())
    # Trim the list to only keep the latest 5 messages
    if len(latest_alert_messages) > 5:
        latest_alert_messages = latest_alert_messages[:5]
    return "Message updated successfully"

@app.route('/download_pdf')
def download_pdf():
    # Create a PDF dynamically
    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer)

    # Write the latest messages and their sentiments to the PDF
    y_position = 750
    for message in latest_alert_messages:
        position, leverage, symbol, entry_price, volume, time_frame, tp1, tp2, tp3, time = extract_info(message)
        c.drawString(50, y_position, f"âš”ï¸ Position: {position}")
        c.drawString(50, y_position - 20, f"ðŸ”— Leverage: {leverage}")
        c.drawString(50, y_position - 40, f"ðŸ“ˆ Symbol: {symbol}")
        c.drawString(50, y_position - 60, f"ðŸ’° Entry Price: {entry_price}")
        c.drawString(50, y_position - 80, f"ðŸ“Š Volume: {volume}")
        c.drawString(50, y_position - 100, f"ðŸ•’ Time Frame: {time_frame}")
        c.drawString(50, y_position - 120, f"ðŸŽ¯ Take Profit Targets:")
        c.drawString(60, y_position - 140, f"TP1: {tp1}")
        c.drawString(60, y_position - 160, f"TP2: {tp2}")
        c.drawString(60, y_position - 180, f"TP3: {tp3}")
        c.drawString(50, y_position - 200, f"â° Time: {time}")
        y_position -= 240  # Adjust the decrement value for the new line

    c.save()

    # Prepare the response with PDF data
    response = make_response(pdf_buffer.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=latest_alerts.pdf'
    response.headers['Content-Type'] = 'application/pdf'

    return response

def extract_info(text):
    position = None
    leverage = None
    symbol = None
    entry_price = None
    volume = None
    time_frame = None
    tp1 = None
    tp2 = None
    tp3 = None
    time = None
    lines = text.split('\n')
    for line in lines:
        parts = line.split(':')
        if len(parts) == 2:
            attribute = parts[0].strip().lower()
            value = parts[1].strip()
            if 'position' in attribute:
                position = value
            elif 'leverage' in attribute:
                leverage = value
            elif 'symbol' in attribute:
                symbol = value
            elif 'entry price' in attribute:
                entry_price = value
            elif 'volume' in attribute:
                volume = value
            elif 'time frame' in attribute:
                time_frame = value
            elif 'tp1' in attribute:
                tp1 = value
            elif 'tp2' in attribute:
                tp2 = value
            elif 'tp3' in attribute:
                tp3 = value
            elif 'time' in attribute:
                if value:
                    time = datetime.fromisoformat(value).strftime("%Y-%m-%d %H:%M:%S")
    return position, leverage, symbol, entry_price, volume, time_frame, tp1, tp2, tp3, time

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
