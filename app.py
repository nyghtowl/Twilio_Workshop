import os

from flask import Flask, session, g
from flask import Response
from flask import request
from flask import render_template
from twilio import twiml
from twilio.rest import TwilioRestClient
from twilio.util import TwilioCapability


# Pull in configuration from system environment variables
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_NUMBER = os.environ.get('TWILIO_NUMBER')

# create an authenticated client that can make requests to Twilio for your
# account.
client = TwilioRestClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Create a Flask web app
app = Flask(__name__)

app.secret_key = 'key'

# Render the home page
@app.route('/')
def index():
    return render_template('index.html')

# Handle a POST request to send a text message. This is called via ajax
# on our web page
@app.route('/message', methods=['POST'])
def message():
    # Send a text message to the number provided
    message = client.sms.messages.create(to=request.form['to'],
                                         from_=TWILIO_NUMBER,
                                         body='Good luck on your Twilio quest!')

    # Return a message indicating the text message is enroute
    return 'Message on the way!'

# Handle a POST request to make an outbound call. This is called via ajax
# on our web page
@app.route('/call', methods=['POST'])
def call():
    # Make an outbound call to the provided number from your Twilio number
    call = client.calls.create(to=request.form['to'], from_=TWILIO_NUMBER, 
                               url='http://twimlets.com/message?Message%5B0%5D=http://demo.kevinwhinnery.com/audio/zelda.mp3')

    # Return a message indicating the call is coming
    return 'Call inbound!'

# Generate TwiML instructions for an outbound call
@app.route('/hello')
def hello():
    response = twiml.Response()
    response.say('Hello there! You have successfully configured a web hook.')
    response.say('Good luck on your Twilio quest!', voice='woman')
    return Response(str(response), mimetype='text/xml')

@app.route('/incoming/sms')
def income_sms():
    response = twiml.Response()
    response.sms('I just responded to a text message. Huzzah!')
    return Response(str(response), mimetype='text/xml')
 
# @app.route('/incoming/call')
# def income_call():
#     response = twiml.Response()
#     # response.say('I just responded to a phone call. Huzzah!', voice='man')
#     with response.gather(numDigits=1, action="/handle-key", method="POST") as g:
#         g.say("""Welcome to ACME widgets, press 1 for support. Press 2 for sales. Press 3 to leave a message. Press 4 to playback the last message. Press 5 to playback all messages. Press 0 to talk to a human.""")
#     return Response(str(response), mimetype='text/xml')

# @app.route('/handle-key', methods=['GET', 'POST'])
# def handle_key():
#     response = twiml.Response()
#     digit_pressed = request.values.get('Digits', None)
#     if digit_pressed == "1":
#         response.say('You selected support. Hanging up now', voice='man')
#         return Response(str(response), mimetype='text/xml')
#     elif digit_pressed == "2":
#         response.say('You selected salse. Hanging up now', voice='man')
#         return Response(str(response), mimetype='text/xml')
#     elif digit_pressed == "3":
#         response.say("Record your message after the tone.")
#         response.record(maxLength="30", action="/handle-recording")
#         return Response(str(response), mimetype='text/xml')
#     elif digit_pressed == "4":
#         for recording in client.recordings.list():
#             response.play(recording.uri)
#             return Response(str(response), mimetype='text/xml')
#     elif digit_pressed == "5":
#         for recording in client.recordings.list():
#             response.play(recording.uri)
#         return Response(str(response), mimetype='text/xml')
#     elif digit_pressed == "0":
#         response.dial("+14152157178")
#         return Response(str(response), mimetype='text/xml')
#     else:
#         return redirect('/')

# @app.route("/handle-recording", methods=['GET', 'POST'])
# def handle_recording():
#     """Play back the caller's recording."""
 
#     return request.values.get("RecordingUrl", None)

@voice
    from_num = request.

@app.route("/send_webmsgs", methods=['GET', 'POST'])
def send_webmsgs():
    application_sid = "AP20bdac38a2e8acc56583056d895501fa"

    capability = TwilioCapability(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    capability.allow_client_incoming("nyghtowl")
    capability.allow_client_outgoing(application_sid)
    cap_token = capability.generate()
    print cap_token

    return render_template('send_webmsgs.html', cap_token=cap_token)

if __name__ == '__main__':
    # Note that in production, you would want to disable debugging
    app.run(debug=True)