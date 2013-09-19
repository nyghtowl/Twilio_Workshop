'''
Sample exercises for Twiliocon 

DON'T FORGET TO UPDATE THE ROUTE ON TWILIO DASHBOARD - esp if running off ngrok
'''
import os

from flask import Flask, flash
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
TWILIO_APP_SID = os.environ.get('TWILIO_APP_SID')
default_number = "4153296152"
default_client = "nyghtowl"

# create an authenticated client that can make requests to Twilio for your
# account.
client = TwilioRestClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Create a Flask web app
app = Flask(__name__)

app.secret_key = 'key'

# Workshop initial code
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

# Challenge 1 - Provides text response to text sent
@app.route('/incoming/sms')
def income_sms():
    response = twiml.Response()
    response.sms('I just responded to a text message. Huzzah!')
    return Response(str(response), mimetype='text/xml')
 
# Challenge 1 & 2
# Setup response for incoming call - first was one response and second provided menu
@app.route('/incoming/call')
def income_call():
    response = twiml.Response()
    # response.say('I just responded to a phone call. Huzzah!', voice='man')
    with response.gather(numDigits=1, action="/handle-key", method="POST") as g:
        g.say("""Welcome to ACME widgets, press 1 for support. Press 2 for sales. Press 3 to leave a message. Press 4 to playback the last message. Press 5 to playback all messages. Press 0 to talk to a human.""")
    return Response(str(response), mimetype='text/xml')

# Challenge 2 & 3
# Handle incoming call menu items
@app.route('/handle-key', methods=['GET', 'POST'])
def handle_key():
    response = twiml.Response()
    digit_pressed = request.values.get('Digits', None)
    if digit_pressed == "1":
        response.say('You selected support. Hanging up now', voice='man')
        return Response(str(response), mimetype='text/xml')
    elif digit_pressed == "2":
        response.say('You selected salse. Hanging up now', voice='man')
        return Response(str(response), mimetype='text/xml')
    elif digit_pressed == "3":
        response.say("Record your message after the tone.")
        response.record(maxLength="30", action="/handle-recording")
        return Response(str(response), mimetype='text/xml')
    elif digit_pressed == "4":
        for recording in client.recordings.list():
            response.play(recording.uri)
            return Response(str(response), mimetype='text/xml')
    elif digit_pressed == "5":
        for recording in client.recordings.list():
            response.play(recording.uri)
        return Response(str(response), mimetype='text/xml')
    elif digit_pressed == "0":
        response.dial("+14152157178")
        return Response(str(response), mimetype='text/xml')
    else:
        return redirect('/')

@app.route("/handle-recording", methods=['GET', 'POST'])
def handle_recording():
    """Play back the caller's recording."""
 
    return request.values.get("RecordingUrl", None)

# Challenge 5 - Make inbound and outbound calls from a webpage
@app.route('/voice', methods=['GET', 'POST'])
def voice():
    from_number = request.values.get('PhoneNumber', None)
    response = twiml.Response()
    # Nest <Client> Twiml inside of a <Dial> verb
    with response.dial(callerId=default_number) as r:
        #If theres a number and it looks like a phone number
        # r.say('Enter the digits on the screen', voice='man')
        if from_number and re.search('^[\d\(\)\- \+]+$', from_number):
            r.number(from_number)
        else:
            r.client(default_client) # Defaults to client
    return Response(str(response), mimetype='text/xml')

@app.route("/send_web_msg", methods=['GET', 'POST'])
def send_web_msg():

    capability = TwilioCapability(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    capability.allow_client_incoming(default_client)
    capability.allow_client_outgoing(TWILIO_APP_SID)
    cap_token = capability.generate()
    print cap_token

    return render_template('send_web_msg.html', cap_token=cap_token, phone_number=default_number)

# Challenge 6 - Find available phone number and offer to purchase if found
@app.route("/find_number")
def find_number():

    numbers = client.phone_numbers.search(area_code="415",
        country="US",
        type="local")
    return render_template('find_number.html', numbers=numbers)

@app.route("/purchase", methods=['POST'])
def purchase():
    # Purchase the first number in the list
    chosen_number = request.form['chosen_number']
    chosen_number.purchase()
    flash ("It was purchased.")
    # return (message=message)

# Hacker Olympics - Receive text messgage to setup for sending to Arduino - 
@app.route("/receive_msg")
def receive_msg():
    for message in client.messages.list():
        print message.body
        print message.messagesid        
        print message.nummedia
        print message.__dict__ # dictionary back of each of these to know keys
        # loop through nummedia to find hte number of pictures
        # print message.mediaurl ?
        # MediaURL1 - provides the picture url
    return ""

# Pusher = Pusher( # Third party solution to post images in demo
#     app_id
#     key
#       ?
# )

@app.route("/incoming")
def incoming():
    for i in range(int(request.form['NumMedia'])):
        media_url = request.form['MediaUrl%i' % i]
        media_content_type = request.form['MediaContentType%i' % i]
        if content_type.startswith('image'):
            pusher['demo'].triggers('image', {'url':media_url}) # Used for demo - put your own place to push content
    return ""


# local host 4040 - gives info on twilio

if __name__ == '__main__':
    # Note that in production, you would want to disable debugging
    app.run(debug=True)