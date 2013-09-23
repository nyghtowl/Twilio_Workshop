'''
Sample exercises for Twiliocon 

DON'T FORGET TO UPDATE THE ROUTE ON TWILIO DASHBOARD - esp if running off ngrok
'''
import os

from flask import Flask
from flask import Response
from flask import request
from flask import render_template, redirect, flash, url_for, session
from twilio import twiml
from twilio.rest import TwilioRestClient
from twilio.util import TwilioCapability
import re

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
app.config.from_object(__name__)

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

def simplify_txt(submitted_txt):
    response_letters = re.sub(r'\W+', '', submitted_txt)
    return response_letters.lower()


# Challenge 4 - Create an sms quiz game
@app.route("/quiz_game")
def quiz_game():
    response = twiml.Response()

    from_number = str(request.values.get('From', None))
    body = request.values.get('Body', None)
    simplify_body = simplify_txt(body)

    print 1, simplify_body
    print 2, from_number

    questions = { 
            0: "What word is shorter when you add two letters to it?",
            1: "What occurs once in a minute, twice in a moment and never in one thousand years?",
            2: "What kind of tree is carried in your hand?",
            3: "Thanks for playing.",
            4: ""
    }

    simplify_answers = { 
            1:"shorter", 
            2:"letterm", 
            3:"palm",
            4:""
            }

    print_answers = { 
            1:"shorter", 
            2:"letter m", 
            3:"palm",
            4:""
            }

    print 3, session

    # if from_number not in track_user:
    if from_number not in session:
        session[from_number] = 0
        counter = session.get('counter', 0)
        counter += 1
        session['counter'] = counter
        message = "Shall we play a game? %s" % questions[0]
    else:
        game_round = session['counter']

        if simplify_answers[game_round] == simplify_body:
            session[from_number] += 10
            score = session[from_number]
            message = "Correct Answer. You have %d points out of 30. %s" % (score, questions[game_round])
        else:
            score = session[from_number]
            message = "Wrong answer. We were looking for %s. Your score is %d out of 30. %s" % (print_answers[game_round], score, questions[game_round])

        session['counter'] += 1

    if session['counter'] > 3:
        session.pop(from_number, None)
        session['counter'] = 0

    print 4, session

    response.sms(message)
    return Response(str(response), mimetype='text/xml')


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
    phone_num =[]
    numbers = client.phone_numbers.search(area_code="415",
        country="US",
        type="local")

    print "find num"
    for number in numbers:
        phone_num.append(number.phone_number)

    return render_template('find_number.html', numbers=phone_num)

@app.route("/purchase", methods=['POST', 'GET'])
def purchase():
    # Purchase the first number in the list
    chosen_number = request.form['chosen_number']
    client.phone_numbers.purchase(phone_number=chosen_number)
    return render_template('purchase.html')

#Bonus
@app.route("/current_number")
def current_number():
    # Print current number
    # number = client.phone_numbers.get(TWILIO_APP_SID)

    numbers = client.phone_numbers.list()
    for number in numbers:
       print number.phone_number
    return ""

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

# Code from Demo about how receive images - has to go through shortcodes
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