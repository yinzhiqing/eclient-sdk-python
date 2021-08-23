#!/usr/bin/python3

import sys, os, time
sys.path.append(os.getcwd())
sys.path.append(f"..")

import web3
from web3 import Web3

class erc1155slot():
    def __init__(self, contract, name = "erc1155"):
        self._contract = contract
        self._name = name

    def slot_name():
        return self._name

    def name(self):
        return self.slot_name()

    def symbol(self):
        return self.slot_name()

    def decimals(self):
        return 0

    def tokenCount(self):
        return self._contract.functions.tokenCount().call()

    def tokenTotleAmount(self, id):
        return self._contract.functions.tokenTotleAmount(id).call()

    def token_id(self, index):
        return self._contract.functions.tokenId(index).call()

    def token_exists(self, id):
        return self._contract.functions.tokenExists(id).call()

    def uri(self):
        return self._contract.functions.uri().call()

    def balance_of(self, account, **kwargs):
        return self._contract.functions.balanceOf(Web3.toChecksumAddress(account), kwargs.get("id")).call()

    def balance_of_batch(self, accounts, **kwargs):
        return self._contract.functions.balanceOfBatch(accounts, kwargs.get("ids")).call()

    def approve(self, spender, value):
        return self._contract.functions.setApprovalForAll(Web3.toChecksumAddress(spender), value).call()

    def allowance(self, owner, spender):
        return self._contract.functions.isApprovalForAll(Web3.toChecksumAddress(owner), Web3.toChecksumAddress(spender)).call()
    
    def pause(self):
        return self._contract.functions.pause().call()

    def unpause(self):
        return self._contract.functions.unpause().call()

    def raw_transfer_from(self, from, to, id, amount, data = None):
        return self._contract.functions.safeTransferFrom(from, to, id, amount, data)

    def raw_transfer_from_batch(self, from, to, ids, amounts, data = None):
        return self._contract.functions.safeBatchTransferFrom(from, to, ids, amounts, data)

    def raw_approve(self, spender, value):
        return self._contract.functions.setApprovalForAll(Web3.toChecksumAddress(spender), value)

    def raw_mint(to, id, amount, data = None):
        return self._contract.functions.mint(to, id, amount, data)

    def raw_mint_batch(to, ids, amounts, data = None):
        return self._contract.functions.mintBatch(to, ids, amounts, data)

    def raw_burn(account, id, amount):
        return self._contract.functions.burn(account, id, amount)

    def raw_burn_batch(account, ids, amounts):
        return self._contract.functions.burnBatch(account, ids, amounts)
   
def test():

    host = "https://kovan.infura.io/v3/2645261bd8844d0c9ac042c84606502d"
    w3 = Web3(Web3.HTTPProvider(host))
    #if not w3.isConnected():
    #    raise Exception("not connect {host}")
    print("connect ok")
    print(f'''
    block number: {w3.eth.blockNumber}
    syncing: {w3.eth.syncing}
    ''')



    
if __name__ == "__main__":
    test()
