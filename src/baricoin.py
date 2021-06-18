import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse

from werkzeug.wrappers import response


class Blockchain:
    def __init__(self) -> None:
        self.chain = []
        self.transactions = []
        self.create_block(proof=1, previous_hash='0')
        self.nodes = set()

    def create_block(self, proof, previous_hash):
        '''Create chain block '''
        block = {'index': len(self.chain)+1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash,
                 'transactions': self.transactions}
        self.transactions = []
        self.chain.append(block)
        return block

    def get_previous_block(self):
        '''Get Previous Block'''
        return self.chain[-1]

    def proof_of_work(self, previous_proof):
        '''Brute force the proof to meet the target '''
        new_proof = 1
        check_proof = False
        while not check_proof:
            # operation should ne asumtrical
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
                break
            new_proof += 1
        return new_proof

    def hash(self, block):
        '''this function to generate the hash for each block'''
        # Encode to get the b so we can run the sha256 script
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def is_chain_valid(self, chain):
        ''' Check if each block hash link to the previous one and if all prood of all block are valid'''
        block_index = 1
        previous_block = chain[0]
        while block_index < len(chain):
            block = chain[block_index]
            if self.hash(previous_block) != block['previous_hash']:
                return False
            previous_proof = previous_block['proof']
            proof = block['block']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True

    def add_transaction(self, sender, receiver, amount):
        ''' Add a transaction '''
        self.transactions.append({'sender': sender,
                                  'receiver': receiver,
                                  'amount': amount})
        return self.get_previous_block()['index']+1

    def add_node(self, address):
        ''' Add a node to the blockchain '''
        self.nodes.add(urlparse(address).netloc)

    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = request.get(f'https://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True

        return False


# Creating a Web App from flask import Flask
app = Flask(__name__)

# Create an address for the node on Port 5000
node_address = str(uuid4()).replace('-', '')

# Create a blockchain
blockchain = Blockchain()


@app.route('/', methods=['GET'])
def route():
    ''' This Method is to mine a block in the block chain '''
    return '<p> <h1>Blockchain demo </h1> <ul><li> <a href="/mine_block">Mine Block</a></li><li><a href="/get_chain">Get Chain</a></li></ul> </p>', 200

# Mining a new Block


@app.route('/mine_block', methods=['GET'])
def mine_block():
    ''' This Method is to mine a block in the block chain '''
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof=previous_proof)
    new_block = blockchain.create_block(proof, blockchain.hash(previous_block))
    blockchain.add_transaction(sender=node_address, receiver='Issam', amount=1)
    response = {'message': 'Congratulation., you just mined a block!',
                'index': new_block['index'],
                'timestamp': new_block['timestamp'],
                'proof': new_block['proof'],
                'previous_hash': new_block['previous_hash'],
                'key': new_block['transactions']}
    return jsonify(response), 200


@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    json = request.get_json()
    transactions_keys = ['sender', 'receiver', 'amount']
    if not all(key in json for key in transactions_keys):
        return 'Transaction key missing', 400
    index = blockchain.add_transaction(json['sender'], json['receiver'], json['amount'])
    response = {'message': f'Transaction will be added to Block {index}'}
    return response, 201


@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200


@app.route('/is_valid', methods=['GET'])
def is_valid():
    response = {'is_valid': blockchain.is_chain_valid(blockchain.chain)}
    return jsonify(response), 200


@app.route('/connect_node', methods=['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return "No node", 400
    for node in nodes:
        blockchain.add_node(node)
    return {'message': 'All the nodes are now connected',
            'total_nodes': list(blockchain.nodes)}


@app.route('/replace_chain', methods=['GET'])
def replace_chain():
    response = {'is_chain_replaced': blockchain.replace_chain()}
    return jsonify(response), 200


app.run(host='0.0.0.0', port=5000)
app.run(host='0.0.0.0', port=5001)
app.run(host='0.0.0.0', port=5002)
app.run(host='0.0.0.0', port=5003)
