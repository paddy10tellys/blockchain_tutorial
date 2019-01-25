import hashlib as hl
import json

def hash_string_256(string):
    return hl.sha256(string).hexdigest()

def hash_block(block):   # hashes block nb block is a dictionary
    ''' sorts keys before dumping block to a string nb the order matters '''

    # return '-'.join([str(block[key]) for key in block])
    # return hl.sha256(json.dumps(block, sort_keys=True).encode()).hexdigest()

    return hash_string_256(json.dumps(block, sort_keys=True).encode())
    # json dumps -> returns a string representing a json object from an object
