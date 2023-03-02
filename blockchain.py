# Module 1 - Create a BlockChain
"""
Created on Wed Mar  1 15:23:30 2023

@author: Arbuchi
"""
# To be installed:
# Flask==0.12.2: pip install Flask==0.12.2
# Postman HTTP Client: https://www.getpostman.com/

#Importing the libraries
import datetime
#for Time-Stamp
import hashlib
import json
from flask import Flask, jsonify

# Part 1 - Building a Blockchain

class Blockchain:
    
    def __init__(self):
        #全部的區塊
        self.chain = []
        #製作新的區塊(PoW值 , 前一個區塊的Hash值)
        self.create_block(proof = 1 , prev_hash = '0')

    #建立新的區塊
    def create_block(self , proof , prev_hash):
        block = {'index': len(self.chain) + 1 ,
                 'timestamp': str(datetime.datetime.now()) ,
                 'proof': proof,
                 'prev_hash': prev_hash
            }
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

# Part 2 - Mining our Blockchain

# Creating a Web App
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# Creating a Blockchain
blockchain = Blockchain()

# Mining a new block
@app.route('/mine_block', methods = ['GET'])
def mine_block():
    prev_block = blockchain.get_prev_block()
    prev_proof = prev_block['proof']
    proof = blockchain.proof_of_work(prev_proof)
    prev_hash = blockchain.hash(prev_block)
    block = blockchain.create_block(proof , prev_hash)
    re = {'message' : 'Congratulations, You just find a new block!!',
          'index' : block['index'],
          'timestamp' : block['timestamp'],
          'proof' : block['proof'],
          'prev_hash' : block['prev_hash']}
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


# Running the app
app.run(host = '0.0.0.0', port = 5000)