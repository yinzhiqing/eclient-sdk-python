#!/usr/bin/python3

import sys, os, time
sys.path.append(os.getcwd())
sys.path.append(f"..")

import web3
from web3 import Web3

token_type = "erc721"
class idfields():
    def __init__(self, id):
        self.__parse(id)

    def to_json(self):
        return dict(
                id = self.id
                )

    def __parse(self, id):
        id = self.__convert_to_hex(id)
        setattr(self, "id", id)

    def __parent_token(self):
        return ""

    def __convert_to_int(self, value):
        if value and isinstance(value, str):
            value = Web3.toInt(hexstr = value)
        return value

    def __convert_to_hex(self, value):
        if value and not isinstance(value, str):
            value = Web3.toHex(value)
        return value[2:] if value.lower().startswith("0x") else value

class erc721slot():
    def __init__(self, contract, name = "erc721"):
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

    def uri(self):
        return self._contract.functions.uri(0).call()

    def total_supply(self):
        return self._contract.functions.totalSupply().call()

    def balance_of(self, account, **kwargs):
        return self._contract.functions.balanceOf(Web3.toChecksumAddress(account)).call()

    def approved(self, id):
        id = self.__convert_to_int(id)
        return self._contract.functions.getApproved(id).call()
    
    def allowance(self, owner, spender):
        raise Exception("not support")
    
    def token_manager(self):
        return self._contract.functions.tokenManager().call()

    def pause(self):
        return self._contract.functions.pause().call()

    def unpause(self):
        return self._contract.functions.unpause().call()

    def raw_transfer_from(self, fom, to, id, amount = 1, data = None):
        id = self.__convert_to_int(id)
        data = self.__convert_to_bytes(data)
        return self._contract.functions.safeTransferFrom(fom, to, id, data)

    def raw_approve(self, spender, value):
        id = self.__convert_to_int(value)
        return self._contract.functions.approve(Web3.toChecksumAddress(spender), id)

    def raw_mint(self, to, id, amount, data = None, *args, **kwargs):
        tid     = kwargs.get("tid", 0)
        id      = self.__convert_to_int(id)
        tid      = self.__convert_to_int(tid)

        return self._contract.functions.mint(Web3.toChecksumAddress(to), id, tid)

    def raw_burn(self, account, id, amount):
        id = self.__convert_to_int(id)
        return self._contract.functions.burn(Web3.toChecksumAddress(account), id, amount)

    def raw_grant_role(self, role, address):
        role = self.__convert_to_bytes(role)
        return self._contract.functions.grantRole(role, Web3.toChecksumAddress(address))

#*************************************extende********************************************

    def minter_role(self):
        return self.__convert_to_hex(self._contract.functions.MINTER_ROLE().call())

    def pauser_role(self):
        return self.__convert_to_hex(self._contract.functions.PAUSER_ROLE().call())

    def admin_role(self):
        return self.__convert_to_hex(self._contract.functions.DEFAULT_ADMIN_ROLE().call())

    def index_start(self, token_id, **kwargs):
        return 0

    def tokenCount(self):
        return self.total_supply()

    def token_id(self, index):
        index = self.__convert_to_int(index)
        return self.__convert_to_hex(self._contract.functions.tokenByIndex(index).call())

    def token_owner(self, id):
        id = self.__convert_to_int(id)
        return self.__convert_to_hex(self._contract.functions.ownerOf(id).call())

    def token_exists(self, id):
        id = self.__convert_to_int(id)
        return self._contract.functions.tokenExists(id).call()

    def type_count(self):
        return self._contract.functions.countOfType().call()

    def type_exists(self, id):
        id = self.__convert_to_int(id)
        return self._contract.functions.typeIsExists(id).call()

    def type_locked(self, id):
        id = self.__convert_to_int(id)
        return self._contract.functions.typeIsLocked(id).call()

    def type_id(self, index):
        index = self.__convert_to_int(index)
        return self.__convert_to_hex(self._contract.functions.typeByIndex(index).call())

    def type_name(self, index):
        index = self.__convert_to_int(index)
        return self.__convert_to_hex(self._contract.functions.typeByIndex(index).call())

    def type_datas(self, key):
        key = self.__convert_to_int(key)
        return self._contract.functions.typeDatasOfType(key).call()

    def token_type(self, id):
        id = self.__convert_to_int(id)
        return self.__convert_to_hex(self._contract.functions.typeOfToken(id).call())

    def raw_mint_type(self, id, capacity, data):
        id = self.__convert_to_int(id)
        capacity = self.__convert_to_int(capacity)
        data = self.__convert_to_bytes(data)

        return self._contract.functions.appendType(id, capacity, data)

    def raw_lock_type(self, id):
        id = self.__convert_to_int(id)
        return self._contract.functions.lockType(id).call()

    def raw_unlock_type(self, id):
        id = self.__convert_to_int(id)
        return self._contract.functions.unlockType(id).call()

#*************************************internal********************************************#
    def __convert_to_int(self, value):
        if value and isinstance(value, str):
            value = Web3.toInt(hexstr = value)
        return value

    def __convert_to_hex(self, value):
        if value and not isinstance(value, str):
            value = Web3.toHex(value)
        return value[2:] if value.lower().startswith("0x") else value

    def __convert_to_bytes(self, value):
        if value and not isinstance(value, str):
            value = Web3.toBytes(value)
        return b'' if not value else value

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
