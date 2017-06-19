#from __future__ import with_statement   # Only necessary for Python 2.5
from flask import Flask, request, redirect
from twilio.twiml.voice_response import Gather, VoiceResponse

app = Flask(__name__)

callers = { # 090-1234-5678 -> +819012345678
        u"+819012345678": "Yui Aragaki",
        u"+819087654321": "Chiemi Blouson",
}


@app.route('/', methods=['GET', 'POST'])
def welcome_message():
    """Introduction for this app.
    If a phone call comes from the registrant, play the honeyspot message and hang up the call
    """

    resp = VoiceResponse()

    from_number = request.values.get('From', None) 

    if from_number in callers:
        resp.play("https://s3-ap-northeast-1.amazonaws.com/twiliowedding/wedding_honeypot.mp3") # hang up the call
    else:
        resp.play("https://s3-ap-northeast-1.amazonaws.com/twiliowedding/wedding_welcome.mp3")
        resp.redirect('/record')

    return str(resp)

        
@app.route('/record', methods=['GET', 'POST'])
def record():
    """Record voice message from a user"""

    resp = VoiceResponse()
    resp.play("https://s3-ap-northeast-1.amazonaws.com/twiliowedding/wedding_introduction.mp3")
    resp.record(action='/handle-recording',maxLength="60",timeout="60")

    return str(resp)                    


@app.route('/handle-recording', methods=['GET', 'POST'])
def handle_recording():
    """Play back the caller's recording"""
        
    recording_url = request.values.get("RecordingUrl", None)

    resp = VoiceResponse()
    resp.play("https://s3-ap-northeast-1.amazonaws.com/twiliowedding/wedding_play_recorded.mp3")
    resp.play(recording_url)

    # Gather digits.
    g = Gather(action='/handle-key', method='POST', timeout=None, finish_on_key=None, num_digits=1)
    g.play("https://s3-ap-northeast-1.amazonaws.com/twiliowedding/wedding_confirmation.mp3")
    resp.append(g)

    return str(resp)


@app.route('/handle-key', methods=['GET', 'POST'])
def handle_key():
    """Handle key press from a user"""

    resp = VoiceResponse()
    digit_pressed = request.values.get('Digits', None)

    if digit_pressed == '1': # To accept the recored mesasge
        resp.play("https://s3-ap-northeast-1.amazonaws.com/twiliowedding/wedding_thanks.mp3")
    elif digit_pressed == '3': # No acceptance. Record the message again
        resp.redirect('/record')
    else:
        resp.redirect('/handle-recording')

    return str(resp)


if __name__ == "__main__":
    app.run(debug=True)
