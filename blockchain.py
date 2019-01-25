from collections import OrderedDict   # nb data structure used for transactions (to maintain order in the transactions)
from functools import reduce
import hashlib as hl
import json
import pickle

from hash_util import hash_string_256, hash_block


# ---------- global variables ----------
MINING_REWARD = 10

# Don't initialize the genesis block, or the blockchain list, or the open_transactions list up here. Better to do it from within the load_data() function code or from within the load_data() except block code if the script cannot find a blockchain.txt file to load...

# the owner of this block chain
owner = 'pmy'

participants = {'pmy'}  # this is actually declaring a set

waiting_for_input = True  # controls the user interface while loop
# ---------- end global variables ----------






# ---------- functions ----------

def save_data():
    try:

        with open('blockchain.txt', mode='w') as f:
            f.write(json.dumps(blockchain))  # serialize a list of blocks which are OrderedDicts into a byte string then write to file
            f.write('\n') # write new line to file
            f.write(json.dumps(open_transactions)) # serialize a list of transactions which are OrderedDicts into a byte string then write to file

        # PICKLE IMPLENTATION
        # with open('blockchain.p', mode='wb') as f:  # b enables binary write
        #     save_data = {
        #         'chain': blockchain,
        #         'ot': open_transactions
        #     }
        #     f.write(pickle.dumps(save_data))


        '''json serialization transforms data into a series of bytes (hence serial) to be stored or transmitted across a network

        NB json.dump and json.load convert between files and object whereas json.dumps and json.loads convert between strings and objects
        '''
    except IOError:
        print('Saving Failed!')

def load_data():
    global blockchain
    global open_transactions
    try:  # to load existing blockchain
        with open('blockchain.txt', mode='r') as f:
            file_content = f.readlines()  # nb this gives a list of strings which will have to be converted...

            blockchain = json.loads(file_content[0][:-1])  # ditch the newline char

            # convert the loaded data from string object to OrderedDict object because Transactions should use OrderedDict
            updated_blockchain = []  # converted blocks end up in here

            '''
            get each block, convert each block, then append block to the updated_blockchain list. When done assign to the blockchain variable which is the actual blockchain...
            '''
            for block in blockchain:
                updated_block = {
                'previous_hash': block['previous_hash'],
                'index': block['index'],
                'proof': block['proof'],
                'transactions': [OrderedDict(
                    [('sender', tx['sender']), ('recipient', tx['recipient']), ('amount', tx['amount'])]) for tx in block['transactions']]
                }
                updated_blockchain.append(updated_block)
            blockchain = updated_blockchain

            open_transactions = json.loads(file_content[1])

            # Similarly transactions are also OrderedDicts so convert from string object to OrderedDict object
            updated_open_transactions = []
            for tx in open_transactions:
                updated_tx = OrderedDict(
                    [('sender', tx['sender']), ('recipient', tx['recipient']), ('amount', tx['amount'])])

                updated_open_transactions.append(updated_tx)
            open_transactions = updated_open_transactions
    except (IOError, IndexError):
        # Initialize (empty) blockchain list if it doesn't exist IOError. NB TODO handle IndexError which is called in attempting to load an empty file
        genesis_block = {
            'previous_hash': '',  # not actually calculating a real # in the GB
            'index': 0,
            'transactions': [],
            'proof': 100  # dummy value for placeholder
        }

        # Add genesis block as first block in the blockchain nb blocks are now OrderedDicts
        blockchain = [genesis_block]  # blockchain needs to be ordered & mutable, so blockchain is a list...

        # as yet unhandled transactions
        open_transactions = []  # transactions awaiting verification need to be mined which requires a function that does mining e.g., see mine_block()
    finally:
        print('Clean up!')

    # PICKLE IMPLEMENTATION
    # with open('blockchain.p', mode='rb') as f:
    #     file_content = pickle.loads(f.read())  # gives a list of strings
    #     global blockchain  # don't want local variablesw created in here
    #     global open_transactions  # we want the global variables defined at the top of the file
    #     blockchain = file_content['chain']
    #     open_transactions = file_content['ot']

load_data()  #  run immediately

# this validation function needs a big while loop
def valid_proof(transactions, last_hash, proof):
    '''  confirms proof: small enough number from the hashing function '''
    guess = (str(transactions) + str(last_hash) + str(proof)).encode()
    guess_hash = hash_string_256(guess) # this is not the hash of the last block! This is the pow # attempting to solve the puzzle!
    print(guess_hash)  # typically prints out loads of hashes
    return guess_hash[0:2] == '00'  # truth condition for a valid hash


# this pow function is just a big while loop
def proof_of_work():
    ''' generates potential proofs '''
    last_block = blockchain[-1]  # the last block
    last_hash = hash_block(last_block)  # hashes block to a string
    proof = 0
    while not valid_proof(open_transactions, last_hash, proof):
        proof += 1  # keep trying different proofs until a winner is found and valid_proof() returns true
    return proof  # the winning number

def get_balance(participant):
    # a list comprehension is a list created from existing lists

    # tx_sender is a list that records every amount ever sent by a participant regardless of the block that it ended up in
    tx_sender = [[tx['amount'] for tx in block['transactions'] if tx['sender']
    == participant] for block in blockchain] # nb tx is a list containing exactly one float value obtained from the transaction dict

    # open_tx_sender is a list that holds any open transactions for a particular participant
    open_tx_sender =[tx['amount'] for tx in open_transactions if tx['sender'] == participant]

    # update the historical transaction amounts record with the participants open transaction amounts
    tx_sender.append(open_tx_sender)

    # the reduce function accepts a function and a sequence and returns a single value
    # Syntax: reduce(function, sequence[, initial]) -> value
    amount_sent = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_sender, 0)  # nb 3rd arg start at 0, 2nd arg is the list of transactions, 1st arg is a lambda with an inline if else(ternary) statement

    # Initially, the lambda function is called with the first two items from the sequence and the result is returned

    # The lambda is then called again with the result obtained in step 1 and the next value in the sequence. This process keeps repeating until all amounts in the sequence have been summed

    ##########################################################################
    # THE ABOVE DOES THE SAME AS THIS COMMENTED OUT CODE
    # amount_sent = 0
    # tx_sender is list of tx which are single item lists containing an amount
    # for tx in tx_sender:  # for each element in this list
    #     if len(tx) > 0:  # an amount was actually sent
    #         amount_sent += tx[0] # nb need the index to get the amount
    ##########################################################################

    tx_recipient = [[tx['amount'] for tx in block['transactions'] if tx['recipient'] == participant] for block in blockchain]

    amount_received = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_recipient, 0)


    # amount_received = 0;
    # for tx in tx_recipient:  # for each element in this list
    #     if len(tx) > 0:  # an amount was actually received
    #         amount_received += tx[0]

    return amount_received - amount_sent


def get_last_blockchain_value():
    """ Returns the last value of the current blockchain. """
    if len(blockchain) < 1:
        return None
    return blockchain[-1]

# This function accepts two arguments.
# One required one (transaction_amount) and one optional one (last_transaction)
# The optional one is optional because it has a default value => [1]

def verify_transaction(transaction):
    sender_balance = get_balance(transaction['sender'])
    return sender_balance >= transaction['amount']


def add_transaction(recipient, sender=owner, amount=1.0):
    """
    Arguments:
    sender
    recipient
    amount

    """
    # transaction = {
    #     'sender': sender,
    #     'recipient': recipient,
    #     'amount': amount
    # }

    #  nb change transaction from dictionary to OrderedDict as dicts are unordered map
    transaction = OrderedDict([('sender', sender), ('recipient', recipient), ('amount', amount)])
    if verify_transaction(transaction):
        open_transactions.append(transaction)
        participants.add(sender)
        participants.add(recipient)
        save_data()   #  whenever the blockchain changes...
        return True  # return statements enable error messaging
    return False

def mine_block():
    """ Create a new block and open transactions to it. """
    last_block = blockchain[-1]
    hashed_block = '' # an empty block
    hashed_block = hash_block(last_block)
    #print(hashed_block)
    proof = proof_of_work() #  nb needs to be before we add reward
    # reward_transaction = {
    #     'sender': 'MINING',
    #     'recipient': owner,
    #     'amount': MINING_REWARD
    # }
    reward_transaction = OrderedDict([('sender', 'MINING'), ('recipient', owner), ('amount', MINING_REWARD)])
    # initially the list of transactions needs to be managed locally rather than globally so copy the open_transactions list by value using range selector to a new list called copied_transactions
    copied_transactions = open_transactions[:] # nb copied by *value*

    # then append the reward transaction to copied_transactions rather than open_transactions
    copied_transactions.append(reward_transaction)  # add reward before mining block

    # then add copied_transactions to the block rather than open_transactions
    block = {
        'previous_hash': hashed_block,
        'index': len(blockchain),
        'transactions': copied_transactions,  # nb local not global
        'proof': proof
    }
    blockchain.append(block)
    return True

def get_transaction_value():
    """ Returns the input of the user (a new transaction amount) as a float. """
    # Get the user input, transform it from a string to a float and store it in user_input
    tx_recipient = input('Enter the recipient of the transaction: ')
    tx_amount = float(input('Your transaction amount please: '))
    return (tx_recipient, tx_amount)


def get_user_choice():
    """Prompts the user for its choice and return it."""
    user_input = input('Your choice: ')
    return user_input


def print_blockchain_elements():
    """ Output all blocks of the blockchain. """
    # Output the blockchain list to the console
    for block in blockchain:
        print('Outputting Block')
        print(block)
    else:
        print('-' * 20)

def print_blockchain_participants():
    print(participants)


def verify_chain():
    """ Verify the current blockchain and return True if it's valid, False otherwise."""

    # loop over blockchain with an automatic counter
    for (index, block) in enumerate(blockchain):
        if index == 0:  # this index refers to the genesis block
            continue  # skip - genesis block has no previous block to check!

        # compare the newly recalculated hash of the preceding block with the current block previous_hash attribute
        if block['previous_hash'] != hash_block(blockchain[index -1]):
            return False

        # redo the pow calculation on the current block by hashing a concatenation of current block open transactions/last_hash/proof inside valid_proof() until winning hash found i.e., the number in the proof arg leads to a hash that starts with '00'

        if not valid_proof(block['transactions'][:-1], block['previous_hash'], block['proof']):  # [:-1] range finder removes the reward prev added to block as this is not a proper transaction
            print('Proof of work is invalid')
            return False
    return True

def verify_transactions():
    """ check that all transactions valid """
    all([verify_transaction(tx) for tx in open_transactions])


# A while loop for the user input interface
# It's a loop that exits once waiting_for_input becomes False or when break is called
while waiting_for_input:
    print('Please choose')
    print('1: Add a new transaction value')
    print('2: Mine Block')
    print('3: Output the blockchain blocks')
    print('4: Output participants')
    print('5: Check transaction validity')
    print('h: Manipulate the chain')
    print('q: Quit')
    user_choice = get_user_choice()
    if user_choice == '1':
        tx_data = get_transaction_value()
        recipient, amount = tx_data  # tuple unpacking
        # Add the transaction data to the blockchain
        if add_transaction(recipient, amount=amount):
            print('Transaction added!')
        else:
            print('Transaction failed!')
        print(open_transactions)
    elif user_choice == '2':
        if mine_block():
            open_transactions = []  # reset to empty list after mining
            save_data()   #  whenever the blockchain changes...
    elif user_choice == '3':
        print_blockchain_elements()
    elif user_choice == '4':
        print_blockchain_participants()
    elif user_choice == '5':
        if verify_transactions():
            print('All transactions are valid!')
        else:
            print('There are invalid transactions!')
    elif user_choice == 'h':
        # Make sure that you don't try to "hack" the blockchain if it's empty
        if len(blockchain) >= 1:
            blockchain[0] = {
                'previous_hash': '',
                'index': 0,
                'transactions': [{'sender':'Chris',
                                     'recipient':'Paddy',
                                         'amount':100.0}]
            }
    elif user_choice == 'q':
        # This will lead to the loop to exist because it's running condition becomes False
        waiting_for_input = False
    else:
        print('Input was invalid, please pick a value from the list!')
    if not verify_chain():
        print_blockchain_elements()
        print('Invalid blockchain!')
        # Break out of the loop
        break
    print('Balance of {}: {:6.2f}'.format('pmy', get_balance('pmy')))
else:
    print('User left!')


print('Done!')
