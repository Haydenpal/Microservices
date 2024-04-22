from flask import Flask, request, render_template, make_response
from io import BytesIO
from reportlab.pdfgen import canvas

app = Flask(__name__)

# Global variable to store the latest messages
latest_alert_messages = ["No alerts triggered yet."] * 5

# Updated URL for the Telegram service
TELEGRAM_SERVICE_URL = 'http://20.198.10.178:8001/webhook'

@app.route('/')
def index():
    return render_template('index.html', latest_alert_messages=latest_alert_messages)

@app.route('/update_message', methods=['POST'])
def update_message():
    global latest_alert_messages
    # Shift the existing messages by one position
    latest_alert_messages = latest_alert_messages[1:] + [request.data.decode('utf-8')]
    
    return "Messages updated successfully"

@app.route('/download_pdf')
def download_pdf():
    # Create a PDF dynamically
    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer)

    # Write the latest messages to the PDF
    y_position = 750
    for message in latest_alert_messages:
        position, symbol, entry_price, time_frame, time, leverage, tp1, tp2, tp3 = extract_info(message)
        c.drawString(50, y_position, f"Position: {position}")  # Add Position information
        c.drawString(50, y_position - 20, f"Symbol: {symbol}")
        c.drawString(50, y_position - 40, f"Entry Price: {entry_price}")
        c.drawString(50, y_position - 60, f"Time Frame: {time_frame}")
        c.drawString(50, y_position - 80, f"Time: {time}")
        c.drawString(50, y_position - 100, f"Leverage: {leverage}")
        c.drawString(50, y_position - 120, f"TP1: {tp1}")
        c.drawString(50, y_position - 140, f"TP2: {tp2}")
        c.drawString(50, y_position - 160, f"TP3: {tp3}")
        y_position -= 180  # Adjust the decrement value for the new line

    c.save()

    # Prepare the response with PDF data
    response = make_response(pdf_buffer.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=latest_alerts.pdf'
    response.headers['Content-Type'] = 'application/pdf'

    return response

def extract_info(text):
    position = None
    symbol = None
    entry_price = None
    time_frame = None
    time = None
    leverage = None
    tp1 = None
    tp2 = None
    tp3 = None
    lines = text.split('\n')
    for line in lines:
        if 'position' in line.lower():
            position = line.split(':')[1].strip()
        elif 'symbol' in line.lower():
            symbol = line.split(':')[1].strip()
        elif 'entry price' in line.lower():
            entry_price = line.split(':')[1].strip()
        elif 'time frame' in line.lower():
            time_frame = line.split(':')[1].strip()
        elif 'time' in line.lower():
            time = line.split(':')[1].strip()
        elif 'leverage' in line.lower():
            leverage = line.split(':')[1].strip()
        elif 'tp1' in line.lower():
            tp1 = line.split(':')[1].strip()
        elif 'tp2' in line.lower():
            tp2 = line.split(':')[1].strip()
        elif 'tp3' in line.lower():
            tp3 = line.split(':')[1].strip()
    return position, symbol, entry_price, time_frame, time, leverage, tp1, tp2, tp3

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
