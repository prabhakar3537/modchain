import datetime
import json
import random
import requests
from flask import render_template, redirect, request
import app.globals as globals
from app import app

# The node with which our application interacts, there can be multiple
# such nodes as well.
it = 0
LOCALHOST = "http://127.0.0.1:"
LEADER_NODE = 8000
#CONNECTED_NODE_ADDRESS = LOCALHOST+str(LEADER_NODE)

posts = []

def get_leader():
    #print("GET LEADERRRRRRRRRRRRR NEW AND IMPROVED")
    res = random.randint(0,9)
    with open('app/globals.json', 'r+') as f:
        data = json.load(f)
        res = data['CURRENT_LEADER']
        f.seek(0)     
        json.dump(data, f, indent=4)
        f.truncate() 
    return res

def fetch_posts():
    """
    Function to fetch the chain from a blockchain node, parse the
    data and store it locally.
    """
    #print("Fetch posts function")
    global LEADER_NODE
    global it
    #it = (it+1)%10
    #print(it)
    CONNECTED_NODE_ADDRESS = LOCALHOST+str(LEADER_NODE+get_leader())
    print("CONNECTED NODE ADDRESS: ")
    print(CONNECTED_NODE_ADDRESS)
    get_chain_address = "{}/chain".format(CONNECTED_NODE_ADDRESS)
    response = requests.get(get_chain_address)
    if response.status_code == 200:
        content = []
        chain = json.loads(response.content)
        for block in chain["chain"]:
            for tx in block["subblocks"]:
                tx["index"] = block["index"]
                tx["hash"] = block["previous_hash"]
                content.append(tx)

        global posts
        posts = sorted(content, key=lambda k: k['timestamp'],
                       reverse=True)


@app.route('/')
def index():
    fetch_posts()
    CONNECTED_NODE_ADDRESS = LOCALHOST+str(LEADER_NODE+get_leader())
    #CONNECTED_NODE_ADDRESS = LOCALHOST+str(LEADER_NODE+node_server.get_leader())
    return render_template('index.html',
                           title='Blockchain for storing IoT Data',
                           posts=posts,
                           node_address=CONNECTED_NODE_ADDRESS,
                           readable_time=timestamp_to_string)


@app.route('/submit', methods=['POST'])
def submit_textarea():
    CONNECTED_NODE_ADDRESS = LOCALHOST+str(LEADER_NODE+get_leader())
    """
    Endpoint to create a new subblock 
    """
    post_content = request.form["content"]
    dev_id = request.form["dev_id"]

    post_object = {
        'dev_id': dev_id,
        'content': post_content,
    }

    # Submit a subblock
    new_tx_address = "{}/new_subblock".format(CONNECTED_NODE_ADDRESS)

    requests.post(new_tx_address,
                  json=post_object,
                  headers={'Content-type': 'application/json'})

    return redirect('/')


def timestamp_to_string(epoch_time):
    return datetime.datetime.fromtimestamp(epoch_time).strftime('%H:%M')
