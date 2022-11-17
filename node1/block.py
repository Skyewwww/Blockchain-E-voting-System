from hashlib import sha256
import json
import math
import time

class Block:

    def __init__(self, index, data, prev_hash, nonce=0, hash=0, difficulty=0, timestamp=int(time.time())):

        # instance variables
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.prev_hash = prev_hash
        self.nonce = nonce
        self.hash = hash
        self.difficulty = difficulty
        

    # compute hash value of this block
    def compute_hash(self):

        # get json string containing info in this block (sort keys to make sure
        # this is repeatable)
        block_header = str(self.index) + str(self.nonce) + str(self.data) + str(self.difficulty) + str(self.timestamp)

        
        # get and return hash of this string using sha256 function (put it into hex form)
        res = sha256(block_header.encode()).hexdigest()
        return res

        # getters and setters
    def get_index(self):
        return self.index
    
    def get_data(self):
        return self.data

    def get_prev_hash(self):
        return self.prev_hash

    def get_nonce(self):
        return self.nonce


    def inc_nonce(self):
        self.nonce += 1

    def get_diff(self):
        return 3 + math.floor(self.index ** (1. / 3))

    # convert to and from json
    def to_json(self):
        return json.dumps(vars(self), sort_keys=True)

    @staticmethod
    def load_json(json_string):
        def decoder(d):
            return Block(d['index'], d['timestamp'], d['data'], d['nonce'], d['difficulty'], d['prev_hash'],  d['hash'])
        return json.loads(json_string, object_hook=decoder)
    
