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

    def slot_name(self):
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
        id = self.__convert_to_int(id)
        return self._contract.functions.tokenTotleAmount(id).call()

    def token_id(self, index):
        return self.__convert_to_hex(self._contract.functions.tokenId(index).call())

    def token_exists(self, id):
        id = self.__convert_to_int(id)
        return self._contract.functions.tokenExists(id).call()

    def uri(self):
        return self._contract.functions.uri(0).call()

    def balance_of(self, account, **kwargs):
        id = self.__convert_to_int(kwargs.get("id"))
        return self._contract.functions.balanceOf(Web3.toChecksumAddress(account), id).call()

    def balance_of_batch(self, accounts, **kwargs):
        ids = self.__convert_ids(kwargs.get("ids"))
        return self._contract.functions.balanceOfBatch(accounts, ids).call()

    def approve(self, spender, approved):
        return self._contract.functions.setApprovalForAll(Web3.toChecksumAddress(spender), approved).call()

    def allowance(self, owner, spender):
        return self._contract.functions.isApprovalForAll(Web3.toChecksumAddress(owner), Web3.toChecksumAddress(spender)).call()
    
    def pause(self):
        return self._contract.functions.pause().call()

    def unpause(self):
        return self._contract.functions.unpause().call()

    def raw_transfer_from(self, fom, to, id, amount, data = None):
        id = self.__convert_to_int(id)
        data = b'' if not data else data
        return self._contract.functions.safeTransferFrom(fom, to, id, amount, data)

    def raw_transfer_from_batch(self, fom, to, ids, amounts, data = None):
        ids = self.__convert_ids(ids)
        data = b'' if not data else data
        return self._contract.functions.safeBatchTransferFrom(fom, to, ids, amounts, data)

    def raw_approve(self, spender, value):
        return self._contract.functions.setApprovalForAll(Web3.toChecksumAddress(spender), value)

    def raw_mint(self, to, id, amount, data = None):
        id      = self.__convert_to_int(id)
        amount  = self.__convert_to_int(amount)
        data = b'' if not data else data
        return self._contract.functions.mint(to, id, amount, data)

    def raw_mint_batch(self, to, ids, amounts, data = None):
        ids = self.__convert_ids(ids)
        return self._contract.functions.mintBatch(to, ids, amounts, data)

    def raw_burn(self, account, id, amount):
        id = self.__convert_to_int(id)
        return self._contract.functions.burn(account, id, amount)

    def raw_burn_batch(self, account, ids, amounts):
        ids = self.__convert_ids(ids)
        return self._contract.functions.burnBatch(account, ids, amounts)
   
#*************************************internal********************************************#
    def __convert_to_int(self, value):
        if value and isinstance(value, str):
            value = Web3.toInt(hexstr = value)
        return value

    def __convert_to_hex(self, value):
        if value and not isinstance(value, str):
            value = Web3.toHex(value)
        return value[2:]

    def __convert_ids(self, ids):
        uids = []
        for id in ids:
            uids.append(self.__convert_to_int(id))
        return uids

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
