import os, random, string, requests, json
from flask import Flask, render_template, redirect, request
from flask_debugtoolbar import DebugToolbarExtension
from urllib import urlencode, urlopen
import re
from channel import Channel


app = Flask(__name__)

app.secret_key = "a_very_dumb_secret"

CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]
MYEMAIL = os.environ["MYEMAIL"]
state = None


@app.route("/")
def index_page():
    """Initial landing page"""

    global state
    state = randomWord()

    params = {"client_id": CLIENT_ID,
                "redirect_uri": "http://localhost:5000/slacked",
                "state": state,
                "team": "Dovetail"}

    oauth_url = "https://slack.com/oauth/authorize?" + urlencode(params)

    return redirect(oauth_url)


@app.route("/slacked")
def slacked():
    """Landing page for authorized slack users"""

    state_returned = request.args.get("state")
    client_code = request.args.get("code")

    if check_state(state_returned) is False:
        return "Slack did not return the expected state variable! You've been h4x0r3d."
    else:
        # OAuth parameters
        params = {"client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                    "code": client_code}

        oauth_url = "https://slack.com/api/oauth.access?" + urlencode(params)
        json_response = requests.get(oauth_url)
        # parse json response
        response = json_response.json()
        # identify user
        user_token = response["access_token"]


        # get list of channels for user
        channel_list = get_channel_list(user_token)

        for channel in channel_list:
            # print channel
            # channel_obj = 

        # # get history for one channel
        # first_channel = channel_list[0]
        # first_channel_history = get_channel_history(user_token, first_channel)
        
        # # convert history into python dictionary
        # msg_dictionary = make_history_dictionary(first_channel_history)

        # # use API call to get sentiment analysis
        # sentiment = get_sentiment(msg_dictionary)

        # print sentiment

    return "authorized"


##################### Helper functions

def randomWord():
    """Generates a random 10 character string, to use as an API verification"""
    return ''.join(random.choice(string.lowercase) for i in range(10))


def check_state(state_returned):
    """Checks that state sent to Slack is correctly returned."""

    if state_returned != state:
        raise Exception("Slack did not return the expected state variable! You've been h4x0r3d.")
        return False
    else:
        return True


def get_channel_list(token):
    """Give a user token, returns a list of tuples with active channel names and ids"""

    channel_params = {"token": token, "exclude_archived": 1}
    channel_url = "https://slack.com/api/channels.list?" + urlencode(channel_params)
    json_channel = requests.get(channel_url)
    channel_response = json_channel.json()

    channel_list = []
    
    for channel in channel_response["channels"]:
        channel_tuple = (channel["name"], channel["id"])
        channel_list.append(channel_tuple)

    return channel_list



if __name__ == '__main__':
    app.run(debug=True)
