from flask import Flask, request, render_template, make_response, redirect, url_for
from io import BytesIO
from reportlab.pdfgen import canvas

app = Flask(__name__)

# Global variables to store the latest messages
latest_alert_messages = ["No alerts triggered yet."] * 5

@app.route('/')
def index():
    reversed_messages_with_info = [extract_info(message) for message in reversed(latest_alert_messages)]
    return render_template('index.html', messages=reversed_messages_with_info)

@app.route('/update_message', methods=['POST'])
def update_message():
    global latest_alert_messages
    message = request.form.get('message')
    position = request.form.get('position')
    symbol = request.form.get('symbol')
    entry_point = request.form.get('entry_point')
    time_frame = request.form.get('time_frame')
    time = request.form.get('time')
    leverage = request.form.get('leverage')
    tp1 = request.form.get('tp1')
    tp2 = request.form.get('tp2')
    
    # Concatenate the message with additional parameters
    full_message = f"{message}\nPosition: {position}\nSymbol: {symbol}\nEntry Point: {entry_point}\nTime Frame: {time_frame}\nTime: {time}\nLeverage: {leverage}\nTP1: {tp1}\nTP2: {tp2}"
    
    latest_alert_messages = latest_alert_messages[1:] + [full_message]
    
    return redirect(url_for('index'))

@app.route('/download_pdf')
def download_pdf():
    # Create a PDF dynamically
    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer)
    
    y_position = 750
    for message in latest_alert_messages:
        entry_point, symbol, _, _, _, _, _, _ = extract_info(message)
        c.drawString(50, y_position, f"Entry Point: {entry_point}")
        c.drawString(50, y_position - 20, f"Symbol: {symbol}")
        c.drawString(50, y_position - 40, f"Time Frame: {time_frame}")
        c.drawString(50, y_position - 60, f"Time: {time}")
        c.drawString(50, y_position - 80, f"Leverage: {leverage}")
        c.drawString(50, y_position - 100, f"TP1: {tp1}")
        c.drawString(50, y_position - 120, f"TP2: {tp2}")
        y_position -= 140
    
    c.save()
    
    response = make_response(pdf_buffer.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=latest_alerts.pdf'
    response.headers['Content-Type'] = 'application/pdf'
    
    return response

def extract_info(text):
    entry_point = None
    symbol = None
    entry_price = None
    time_frame = None
    time = None
    leverage = None
    tp1 = None
    tp2 = None
    lines = text.split('\n')
    for line in lines:
        if 'position' in line.lower():
            entry_point = line.split(':')[1].strip()
        elif 'symbol' in line.lower():
            symbol = line.split(':')[1].strip()
        elif 'entry point' in line.lower():
            entry_point = line.split(':')[1].strip()
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
    return entry_point, symbol, entry_price, time_frame, time, leverage, tp1, tp2

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
