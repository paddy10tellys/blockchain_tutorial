import hashlib as hl
import json
import pdb
Round = 0

# Hash pairs of items recursively until a single value is obtained
def merkle(hashList):  # arg is txHashes2 from the merkle function call see eof
    global Round
    Round = Round + 1  # 1 first round
    if len(hashList) == 1:  # must be the root
        print("AND OUR MERKLE ROOT IS")
        return hashList[0]

    newHashList = []  # holds processed pairs returned by the hash2 function

    print("Number of Nodes in Round", Round, "is", len(hashList))  # Number of Leaves in Round 1 is 10

    # iterate through the hashList (which is the arg txHashes2 passed into the merkle function call at the end of this file) nine times starting with the hash at index zero which is the first hashed transaction, get two consecutive hashes at a time, process the pairs. For odd length, last item is hashed with itself nb all hashes are <str> objects
    for i in range(0, len(hashList)-1, 2):
        print("Node",i+1, "is", hashList[i])  # Leaf 1 is aa123
        print("Node",i+2, "is", hashList[i+1])  # Leaf 2 is bb456

        #  concatenate the left & right child hashes then hash that hash
        print("their hash is", hash2(hashList[i], hashList[i+1]))

        newHashList.append(hash2(hashList[i], hashList[i+1]))
    if len(hashList) % 2 == 1: # odd, hash last item twice
        print("Node", len(hashList), "is", hashList[len(hashList)-1])
        print("And Node",len(hashList),"is hashed with itself to get", hash2(hashList[-1], hashList[-1]))
        newHashList.append(hash2(hashList[-1], hashList[-1]))
    print("DONE with Round", Round)
    print("<========================================================>")
    return merkle(newHashList)


# nb args are hashList[i], hashList[i+1] which are already hashes
def hash2(first, second):
    # reverse inputs before hashing due to big-endian / little-endian nonsense
    firstreverse = first[::-1].encode()  # reverse string then use encode() returns default utf-8 encoded version of the string
    secondreverse = second[::-1].encode()  #  # reverse string then use encode() returns default utf-8 encoded version of the string

    # in Python 3, there is one and only one string type. Its name is str and it’s a Unicode object. Sequences of bytes are now represented by a type called bytes

    # nb .digest() needed because Unicode-objects must be encoded before hashing whereas the hexdigest() is returned as a string object of double length, containing only hexadecimal digits
    h = hl.sha256(hl.sha256(firstreverse+secondreverse).digest()).hexdigest()

    # as bytes
    # b'p\\\xbe\xf8\x97\xf2\xe0\xc9\xfc\xdciZ\xc2\xff^#hP4@\n\xe0\x99\t\x83\xb1\xd49\xe88\xde\n'
    # as string (i.e., Unicode)
    # 705cbef897f2e0c9fcdc695ac2ff5e23685034400ae0990983b1d439e838de0a

    # raise SystemExit  # https://stackoverflow.com/questions/19747371/python-exit-commands-why-so-many-and-when-should-each-be-used

    # reverse inputs after hashing due to big-endian / little-endian nonsense
    return h[::-1]


txHashes2 = ['aa', 'bb', 'cc', 'dd', 'ee', '11', '22', '33', '44', '55']

#pdb.set_trace()

print(merkle(txHashes2))
