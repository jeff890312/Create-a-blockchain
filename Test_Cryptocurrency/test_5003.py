# Module 2 - Create a Cryptocurrency
"""
Created on Tus Apr  11 10:09:30 2023

@author: Arbuchi
"""

# To be installed:
# Flask==0.12.2: pip install Flask==0.12.2
# Postman HTTP Client: https://www.getpostman.com/
# requests==2.18.4: pip install requests==2.18.4

#Importing the libraries
import datetime
#for Time-Stamp
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse


# Part 1 - Building a Blockchain

class Blockchain:
    
    def __init__(self):
        #全部的區塊
        self.chain = []
        #一定要放在create block前面，因為如果放在後面會兩行都跑變成建立區塊時又建立一個交易。
        self.transactions = []
        #製作新的區塊(PoW值 , 前一個區塊的Hash值)
        self.create_block(proof = 1 , prev_hash = '0')
        self.nodes = set()

    #建立新的區塊
    def create_block(self , proof , prev_hash):
        block = {'index': len(self.chain) + 1 ,
                 'timestamp': str(datetime.datetime.now()) ,
                 'proof': proof,
                 'prev_hash': prev_hash,
                 'transactions': self.transactions
            }
        self.transactions = []
        self.chain.append(block)
        return block
    
    #得到上一個區塊的值
    def get_prev_block(self):
        return self.chain[-1]
    
    #Proof-of-Work(PoW)
    def proof_of_work(self, prev_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            #所謂困難的數學題目
            #hexdigest 為hashlib的十六進位法
            hash_operation = hashlib.sha256(str(new_proof**2 - prev_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000' :
                check_proof = True
            else:
                new_proof += 1
        return new_proof
        
    #Hash Block
    def hash(self, block):
        encode_block = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encode_block).hexdigest()
    
    #Verify Blockchain
    def is_chain_valid(self, chain):
        prev_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            #檢查prev_block是否相同
            #因為要使用同一個class裡面的函數hash，所以前面要加入self
            if block['prev_hash'] != self.hash(prev_block):
                return False
            prev_proof = prev_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - prev_proof**2).encode()).hexdigest()
            #檢查前4碼是否符合條件
            if hash_operation[:4] != '0000' :
                return False
            prev_block = block
            block_index += 1
        
        return True
    
    def add_transaction(self, sender, receiver, amount):
        self.transactions.append({'sender':sender,
                                  'recevier':receiver,
                                  'amount':amount})
        prev_block = self.get_prev_block()
        return prev_block['index'] + 1

    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
        
    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_chain = len(longest_chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if requests.status_codes == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_chain and self.is_chain_valid(chain):
                    max_chain = length
                    longest_chain = chain
            if longest_chain:
                self.chain = longest_chain
                return True
            return False
                    
# Part 2 - Mining our Blockchain

# Creating a Web App
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# Creating an address for the node on Port 5000
node_address = str(uuid4()).replace('-', '')

# Creating a Blockchain
blockchain = Blockchain()

# Mining a new block
@app.route('/mine_block', methods = ['GET'])
def mine_block():
    prev_block = blockchain.get_prev_block()
    prev_proof = prev_block['proof']
    proof = blockchain.proof_of_work(prev_proof)
    blockchain.add_transaction(sender = node_address, receiver = 'Jeff', amount = 1)
    prev_hash = blockchain.hash(prev_block)
    block = blockchain.create_block(proof , prev_hash)
    re = {'message' : 'Congratulations, You just find a new block!!',
          'index' : block['index'],
          'timestamp' : block['timestamp'],
          'proof' : block['proof'],
          'prev_hash' : block['prev_hash'],
          'transactions' : block['transactions']}
    return jsonify(re) , 200
    
# Getting the full blockchain
@app.route('/get_blockchain', methods = ['GET'])
def get_blockchain():
    re = {'chain' : blockchain.chain,
          'Length' : len(blockchain.chain)}
    return jsonify(re) , 200
    
# Checking if the Blockchain is valid
@app.route('/is_valid', methods = ['GET'])
def is_valid():
    valid = blockchain.is_chain_valid(blockchain.chain)
    if valid:
        re = {'message': 'Congratulations, the blockchain has completed verification!!'}
    else:
        
        re = {'message': 'No!!! The blockchain has been hacked!!'}
    return jsonify(re) , 200

# Adding a new transaction to the Blockchain
@app.route('/add_transactions', methods = ['POST'])
def add_transactions():
    json = request.get_json()
    transaction_keys = ['sendor', 'recevier', 'amount']
    if not all (key in json for key in transaction_keys):
        return 'Some elements of the transaction are missing', 400
    index = blockchain.add_transaction(json['sender'], json['receiver'], json['amount'])
    response = {'message': f'This transaction will be added to Block {index}'}
    return jsonify(response), 201

# Part 3 - Decentralizaing our Blockchain

# Connecting new nodes
@app.route('/connect_node', methods = ['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return 'No Node', 400
    for node in nodes:
        blockchain.add_node(node)
    response = {'message': 'All the nodes are now connected.',
                'total_nodes' : list(blockchain.nodes)}
    return jsonify(response), 201

# Replacing the chain by the longest chain if needed
@app.route('/replace_chain', methods = ['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        re = {'message': 'The nodes had different chains so the chain wes replaced by the longest one!',
              'new_chain' : blockchain.chain}
    else:
        
        re = {'message': 'All good. The chain is the largest one',
              'actual_chain' : blockchain.chain}
        
    return jsonify(re) , 200
# Running the app
app.run(host = '0.0.0.0', port = 5003)


