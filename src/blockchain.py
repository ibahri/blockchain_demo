import datetime
import hashlib
import json
from flask import Flask, jsonify


class Blockchain:
    def __init__(self) -> None:
        self.chain = []
        self.create_block(proof=1, previous_hash='0')

    def create_block(self, proof, previous_hash):
        '''Crarte  chain block '''
        block = {'index': len(self.chain)+1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash}
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


# Creating a Web App from flask import Flask
app = Flask(__name__)

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
    response = {'message': 'Congratulation., you just mined a block!',
                'index': new_block['index'],
                'timestamp': new_block['timestamp'],
                'proof': new_block['proof'],
                'previous_hash': new_block['previous_hash']}
    return jsonify(response), 200


@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200


@app.route('/is_valid', methods=['GET'])
def is_valid():
    response = {'is_valid': blockchain.is_chain_valid(blockchain.chain)}
    return jsonify(response), 200

app.run(host='0.0.0.0', port=5000)
