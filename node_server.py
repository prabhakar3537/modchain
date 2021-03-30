from hashlib import sha256
import json
import time
from flask import Flask, request
import requests
import random
import app.globals as globals
import time
import math
leader_group = []

def leader_group_size():
    with open('app/globals.json', 'r+') as f:
        data = json.load(f)
        global leader_group
        leader_group =[]
        total = data['NUM']
        num = int(math.ceil(total/(3.5)))
        l = []
        for i in range(num):
            l.append(i)
        leader_group = random.sample(l, num)
        data["leader_group"] = leader_group
        f.seek(0)     
        json.dump(data, f, indent=4)
        f.truncate() 
    return

#Leader election protocol
def update_leader():
    with open('app/globals.json', 'r+') as f:
        data = json.load(f)
        print("OLD LEADER: ")
        print(data['CURRENT_LEADER'])
        data['CURRENT_LEADER'] = start_bid()
        #Ignore lower trust score nodes
        while(data['trust_score'][data["CURRENT_LEADER"]]<0):
            data['CURRENT_LEADER'] = random.randint(0,9)
        print("NEW LEADER: ")
        print(data['CURRENT_LEADER'])
        f.seek(0)     
        json.dump(data, f, indent=4)
        f.truncate() 
    return

#Leader group selection protocol
def update_leader_group():
    with open('app/globals.json', 'r+') as f:
        data = json.load(f)
        leader_group = data['leader_group']
        print("OLD Node Committee: ")
        print(leader_group)
        with open('app/globals.json', 'r+') as f:
            data = json.load(f)
            if(data['CURRENT_LEADER'] in leader_group):
                print(data['CURRENT_LEADER'])
            else:
                credit = data['credit']
                minindex = leader_group[0]
                for i in range(len(leader_group)):
                    if credit[minindex] > credit[leader_group[i]]:
                        minindex = leader_group[i]
                print("Node committee member removed: ")
                print(minindex)
                leader_group.remove(minindex)
                leader_group.append(data["CURRENT_LEADER"])
            print("New Node Committee: ")
            print(leader_group)
            f.seek(0)
            data['leader_group'] = leader_group     
            json.dump(data, f, indent=4)
            f.truncate() 
    return
    
class Block:
    def __init__(self, index, subblocks, timestamp, previous_hash, nonce=0):
        self.index = index
        self.subblocks = subblocks
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce

    def compute_hash(self):
        """
        A function that return the hash of the block contents.
        """
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()


class Blockchain:
    # difficulty of our PoW algorithm
    difficulty = 0
    def __init__(self):
        with open('app/globals.json', 'r+') as f:
            data = json.load(f)
            leader_group = data["leader_group"]
            if len(leader_group)==0:
                for i in range(globals.group_size):
                    leader_group.append(i)
            data['leader_group'] = leader_group
            f.seek(0)     
            json.dump(data, f, indent=4)
            f.truncate() 
        self.unconfirmed_subblocks = []
        self.chain = []

    def create_genesis_block(self):
        genesis_block = Block(0, [], 0, "0")
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)

    def add_core_block(self, proof):
        block = Block(last_block.index+1, [], timestamp=time.time, previous_hash=last_block.hash)
        previous_hash = self.last_block.hash
        if previous_hash != block.previous_hash:
            return False
        if not Blockchain.is_valid_proof(block, proof):
            return False
        block.hash = proof
        self.chain.append(block)
        return True

    @property
    def last_block(self):
        return self.chain[-1]

    def add_block(self, block, proof):
        previous_hash = self.last_block.hash

        if previous_hash != block.previous_hash:
            return False

        if not Blockchain.is_valid_proof(block, proof):
            return False

        block.hash = proof
        self.chain.append(block)
        return True

    @staticmethod
    def proof_of_work(block):
        """
        Function that tries different values of nonce to get a hash
        that satisfies our difficulty criteria.
        """
        block.nonce = 0

        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * Blockchain.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()

        return computed_hash

    def add_new_subblock(self, subblock):
        self.unconfirmed_subblocks.append(subblock)

    @classmethod
    def is_valid_proof(cls, block, block_hash):
        """
        Check if block_hash is valid hash of block and satisfies
        the difficulty criteria.
        """
        return (block_hash.startswith('0' * Blockchain.difficulty) and
                block_hash == block.compute_hash())

    @classmethod
    def check_chain_validity(cls, chain):
        result = True
        previous_hash = "0"

        for block in chain:
            block_hash = block.hash
            # remove the hash field to recompute the hash again
            # using `compute_hash` method.
            delattr(block, "hash")

            if not cls.is_valid_proof(block, block_hash) or \
                    previous_hash != block.previous_hash:
                result = False
                break

            block.hash, previous_hash = block_hash, block_hash

        return result

    def mine(self):
        if not self.unconfirmed_subblocks:
            return False
        t0 = time.time()
        last_block = self.last_block

        new_block = Block(index=last_block.index + 1,
                          subblocks=self.unconfirmed_subblocks,
                          timestamp=time.time(),
                          previous_hash=last_block.hash)

        proof = self.proof_of_work(new_block)
        self.add_block(new_block, proof)
        t1 = time.time() - t0
        with open('app/globals.json', 'r+') as f:
            data = json.load(f)
            time_mod = list(data['time_mod'] )
            time_mod.append(t1)
            data['time_mod'] = time_mod
            f.seek(0)     
            json.dump(data, f, indent=4)
            f.truncate() 
        self.unconfirmed_subblocks = []
        return True


app = Flask(__name__)

# the node's copy of blockchain
blockchain = Blockchain()
blockchain.create_genesis_block()

# the address to other participating members of the network
peers = set()


# endpoint to submit a new subblock. 
@app.route('/new_subblock', methods=['POST'])
def new_subblock():
    tx_data = request.get_json()
    required_fields = ["dev_id", "content"]

    for field in required_fields:
        if not tx_data.get(field):
            return "Invalid subblock data", 404

    tx_data["timestamp"] = time.time()

    blockchain.add_new_subblock(tx_data)

    return "Success", 201


# endpoint to return the node's copy of the chain.
@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)
    return json.dumps({"length": len(chain_data),
                       "chain": chain_data,
                       "peers": list(peers)})


# endpoint to request the node to mine the unconfirmed
# subblocks (if any). We'll be using it to initiate
# a command to mine from our application itself.
@app.route('/mine', methods=['GET'])
def mine_unconfirmed_subblocks():
    result = blockchain.mine()
    update_leader()
    update_leader_group()
    if not result:
        return "No subblocks to mine?"
    else:
        # Making sure we have the longest chain before announcing to the network
        chain_length = len(blockchain.chain)
        consensus()
        if chain_length == len(blockchain.chain):
            # announce the recently mined block to the network
            announce_new_block(blockchain.last_block)
            
        return "Block #{} is mined.".format(blockchain.last_block.index)


# endpoint to add new peers to the network.
@app.route('/register_node', methods=['POST'])
def register_new_peers():
    node_address = request.get_json()["node_address"]
    if not node_address:
        return "Invalid data", 400

    # Add the node to the peer list
    peers.add(node_address)

    # Return the consensus blockchain to the newly registered node
    # so that he can sync
    return get_chain()


@app.route('/register_with', methods=['POST'])
def register_with_existing_node():
    """
    Internally calls the `register_node` endpoint to
    register current node with the node specified in the
    request, and sync the blockchain as well as peer data.
    """
    node_address = request.get_json()["node_address"]
    if not node_address:
        return "Invalid data", 400

    data = {"node_address": request.host_url}
    headers = {'Content-Type': "application/json"}

    # Make a request to register with remote node and obtain information
    response = requests.post(node_address + "/register_node",
                             data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        global blockchain
        global peers
        # update chain and the peers
        chain_dump = response.json()['chain']
        blockchain = create_chain_from_dump(chain_dump)
        peers.update(response.json()['peers'])
        return "Registration successful", 200
    else:
        # if something goes wrong, pass it on to the API response
        return response.content, response.status_code


def create_chain_from_dump(chain_dump):
    generated_blockchain = Blockchain()
    generated_blockchain.create_genesis_block()
    for idx, block_data in enumerate(chain_dump):
        if idx == 0:
            continue  # skip genesis block
        block = Block(block_data["index"],
                      block_data["subblocks"],
                      block_data["timestamp"],
                      block_data["previous_hash"],
                      block_data["nonce"])
        proof = block_data['hash']
        added = generated_blockchain.add_block(block, proof)
        if not added:
            raise Exception("The chain dump is tampered!!")
    return generated_blockchain


# endpoint to add a block mined by someone else to
# the node's chain. The block is first verified by the node
# and then added to the chain.
@app.route('/add_block', methods=['POST'])
def verify_and_add_block():
    block_data = request.get_json()
    block = Block(block_data["index"],
                  block_data["subblocks"],
                  block_data["timestamp"],
                  block_data["previous_hash"],
                  block_data["nonce"])

    proof = block_data['hash']
    added = blockchain.add_block(block, proof)

    if not added:
        return "The block was discarded by the node", 400

    return "Block added to the chain", 201


# endpoint to query unconfirmed subblocks
@app.route('/pending_tx')
def get_pending_tx():
    return json.dumps(blockchain.unconfirmed_subblocks)

def initialize_credit():
    with open('app/globals.json', 'r+') as f:
        data = json.load(f)
        #initializing credit arrays
        credit = []
        size = data['NUM']
        #Iterating for number of nodes
        for i in range(size):
            credit.append(data['initial_credit'])
        #Copying the credit value to shared storage
        data['credit'] = credit
        f.seek(0)     
        json.dump(data, f, indent=4)
        f.truncate() 
    return True       
        

def get_deposit():
    print("Getting deposit: ")
    with open('app/globals.json', 'r+') as f:
        data = json.load(f)
        credit = data['credit']
        current_leader = data['CURRENT_LEADER']
        print("Current leader is: "+str(data['CURRENT_LEADER'])+" with credit of "+str(credit[data['CURRENT_LEADER']]))
        if(credit[current_leader]<data['DEPOSIT']):
            return False
        else:
            print('Getting deposit of '+str(data['DEPOSIT'])+" from leader")
            credit[current_leader]=credit[current_leader]-data['DEPOSIT']
            data['current_deposit'] = data['DEPOSIT']
            print("Credit after deposit: "+str(credit[current_leader]))
        data['credit'] = credit
        f.seek(0)     
        json.dump(data, f, indent=4)
        f.truncate() 
    return True

def return_deposit():
    with open('app/globals.json', 'r+') as f:
        print('Deposit Returned after successful consensus')
        data = json.load(f)
        credit = data['credit']
        credit[data['CURRENT_LEADER']] += data['current_deposit']
        data['current_deposit'] = 0
        data['credit'] = credit
        f.seek(0)     
        json.dump(data, f, indent=4)
        f.truncate() 

def split_credit():
    print("Consensus failed. Splitting credit between node committee")
    with open('app/globals.json', 'r+') as f:
        data = json.load(f)
        credit = data['credit']
        split_up = data['current_deposit']/(data['NUM']-1)
        data['current_deposit'] = 0
        for i in range(data['NUM']):
            if(i == data['CURRENT_LEADER']):
                continue
            credit[i]+=split_up
        data['credit'] = credit
        f.seek(0)     
        json.dump(data, f, indent=4)
        f.truncate() 

def incentive():
    print('Adding Incentive')
    with open('app/globals.json', 'r+') as f:
        data = json.load(f)
        credit = data['credit']
        credit[data['CURRENT_LEADER']] += (0.1* data['DEPOSIT'])
        data['credit'] = credit
        f.seek(0)     
        json.dump(data, f, indent=4)
        f.truncate() 

#Auction Mechanism
def get_bid():
    with open('app/globals.json', 'r+') as f:
        data = json.load(f)
        arr=[]
        for i in range(data["NUM"]):
            arr.append(random.randint(1,100)*5)
        data['bid_amount'] = arr
        f.seek(0)     
        json.dump(data, f, indent=4)
        f.truncate() 

def start_bid():
    print('Starting Private Auction For selection of new leader node')
    get_bid()
    with open('app/globals.json', 'r+') as f:
        data = json.load(f)
        arr = data['bid_amount']
        maxi = 0
        for i in range(len(arr)):
            if arr[i] > arr[maxi]:
                maxi=i
        data["CURRENT_LEADER"] = maxi
        print("Auction winner: "+str(maxi)+"\nWinning Bid: "+str(arr[maxi]))
        f.seek(0)     
        json.dump(data, f, indent=4)
        f.truncate() 
    return maxi

def consensus():
    global blockchain
    longest_chain = None
    current_len = len(blockchain.chain)
    leader_group_peers = []
    leader_group = []
    deposit = get_deposit()
    if deposit == False:
        return False
    with open('app/globals.json', 'r+') as f:
        data = json.load(f)
        leader_group = data['leader_group']
    for i in leader_group:
        format_node = "http://127.0.0.1:"+str(8000+i)+"/"
        leader_group_peers.append(format_node)
    for node in leader_group_peers:
        response = requests.get('{}chain'.format(node))
        length = response.json()['length']
        chain = response.json()['chain']
        if length > current_len and blockchain.check_chain_validity(chain):
            current_len = length
            longest_chain = chain
        if longest_chain:
            blockchain = longest_chain
            #Decrease trust factor
            with open('app/globals.json', 'r+') as f:
                data = json.load(f)
                trust_score = data['trust_score']
                trust_score[data['CURRENT_LEADER']] -= 1
                data["trust_score"] = trust_score
                f.seek(0)     
                json.dump(data, f, indent=4)
                f.truncate() 
            split_credit()
        else:
            #Increase trust factor
            with open('app/globals.json', 'r+') as f:
                data = json.load(f)
                trust_score = data['trust_score']
                trust_score[data['CURRENT_LEADER']] += 1
                data["trust_score"] = trust_score
                f.seek(0)     
                json.dump(data, f, indent=4)
                f.truncate() 
    if longest_chain:
        return True
    return_deposit()
    incentive()
    return False


def announce_new_block(block):
    """
    A function to announce to the network once a block has been mined.
    Other blocks can simply verify the proof of work and add it to their
    respective chains.
    """
    for peer in peers:
        url = "{}add_block".format(peer)
        headers = {'Content-Type': "application/json"}
        requests.post(url,
                      data=json.dumps(block.__dict__, sort_keys=True),
                      headers=headers)

#app.run(debug=True, port=8000)
