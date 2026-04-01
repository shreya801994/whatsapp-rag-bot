from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import os
import threading
import time  # <-- The missing ingredient!
from rag import query_rag
from ingest_url import ingest_from_url

app = Flask(__name__)

TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def process_pdf_background(media_url, sender_id, twilio_id):
    """Processes the PDF in the background without paralyzing the server."""
    time.sleep(2) # Give Flask 2 seconds to send the 200 OK first!
    try:
        ingest_from_url(media_url, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        client.messages.create(from_=twilio_id, to=sender_id, body="Done! Your document is ready. Ask me anything about it.")
    except Exception as e:
        client.messages.create(from_=twilio_id, to=sender_id, body=f"Sorry, failed to process the PDF: {str(e)}")

def background_ai_task(user_msg, sender_id, twilio_id):
    """Runs the AI without choking the web server's CPU."""
    time.sleep(2) # Give Flask 2 seconds to send the 200 OK first!
    try:
        answer = query_rag(user_msg)
        client.messages.create(from_=twilio_id, to=sender_id, body=answer)
    except Exception as e:
        client.messages.create(from_=twilio_id, to=sender_id, body=f"Sorry, I ran into an error while thinking: {str(e)}")

@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    user_msg = request.form.get("Body", "").strip()
    num_media = int(request.form.get("NumMedia", 0))
    sender_whatsapp_id = request.form.get("From")
    twilio_whatsapp_id = request.form.get("To")
    
    resp = MessagingResponse()

    # User sent a PDF
    if num_media > 0:
        media_url = request.form.get("MediaUrl0")
        media_type = request.form.get("MediaContentType0", "")

        if "pdf" in media_type or "document" in media_type:
            # 1. Fire off the background thread
            threading.Thread(target=process_pdf_background, args=(media_url, sender_whatsapp_id, twilio_whatsapp_id), daemon=True).start()
            
            # 2. Instantly return the message (Server doesn't wait!)
            resp.message("Got your PDF! Processing it now in the background, please wait...")
            return str(resp)
        else:
            resp.message("Please send a PDF document.")
            return str(resp)

    # User sent a text question
    if user_msg:
        # 1. Fire off the AI thread
        threading.Thread(target=background_ai_task, args=(user_msg, sender_whatsapp_id, twilio_whatsapp_id), daemon=True).start()
        
        # 2. Instantly return the message (Server doesn't wait!)
        resp.message("Thinking about it... 🧠")
        return str(resp)

    resp.message("Send me a PDF to get started, or ask a question!")
    return str(resp)

if __name__ == "__main__":
    # threaded=True explicitly tells Flask it can handle multiple things at once
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)