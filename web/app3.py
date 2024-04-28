from flask import Flask, request, render_template, make_response
from io import BytesIO
from reportlab.pdfgen import canvas
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

app = Flask(__name__)

# URL of the Telegram Service
TELEGRAM_SERVICE_URL = 'http://20.197.21.223:80/webhook'

# Initialize the sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

# Global variables to store the latest messages and their sentiments
latest_alert_messages = ["No alerts triggered yet."] * 5
latest_sentiments = [""] * 5

@app.route('/')
def index():
    messages_with_info = [extract_info(message) for message in latest_alert_messages]
    messages_with_sentiments = zip(messages_with_info, latest_sentiments)
    return render_template('index.html', messages_with_sentiments=messages_with_sentiments)

@app.route('/update_message', methods=['POST'])
def update_message():
    global latest_alert_messages, latest_sentiments
    # Shift the existing messages and sentiments by one position
    latest_alert_messages = latest_alert_messages[1:] + [request.data.decode('utf-8')]
    
    # Perform sentiment analysis based on keywords indicating profit or loss
    for i, message in enumerate(latest_alert_messages):
        if 'profit' in message.lower():
            latest_sentiments[i] = "Positive"
        elif 'loss' in message.lower():
            latest_sentiments[i] = "Negative"
        else:
            # Perform sentiment analysis using VADER if keywords are not found
            sentiment_score = analyzer.polarity_scores(message)
            if sentiment_score['compound'] >= 0.05:
                latest_sentiments[i] = "Positive"
            elif sentiment_score['compound'] <= -0.05:
                latest_sentiments[i] = "Negative"
            else:
                latest_sentiments[i] = "Neutral"
    
    return "Messages updated successfully"

@app.route('/download_pdf')
def download_pdf():
    # Create a PDF dynamically
    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer)

    # Write the latest messages and their sentiments to the PDF
    y_position = 750
    for message, sentiment in zip(latest_alert_messages, latest_sentiments):
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
        parts = line.split(':')
        if len(parts) == 2:
            attribute = parts[0].strip().lower()
            value = parts[1].strip()
            if 'position' in attribute:
                position = value
            elif 'symbol' in attribute:
                symbol = value
            elif 'entry price' in attribute:
                entry_price = value
            elif 'time frame' in attribute:
                time_frame = value
            elif 'time' in attribute:
                time = value
            elif 'leverage' in attribute:
                leverage = value
            elif 'tp1' in attribute:
                tp1 = value
            elif 'tp2' in attribute:
                tp2 = value
            elif 'tp3' in attribute:
                tp3 = value
    return position, symbol, entry_price, time_frame, time, leverage, tp1, tp2, tp3

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
