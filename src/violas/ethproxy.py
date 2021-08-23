#!/usr/bin/python3
import operator
import sys
import json
import os
sys.path.append("..")
import log
import log.logger
import traceback
import datetime
import stmanage
import requests
import random
import comm
import comm.error
import comm.result
import comm.values
import vmp_main_abi
import vmp_datas_abi
import vmp_state_abi
import usdt_abi
import wbtc_abi
import erc20_std_abi
import erc1155_std_abi
from comm import version
from comm.result import result, parse_except
from comm.error import error
from enum import Enum
from comm.functions import json_print
from ethopt.erc20slot import erc20slot 
from ethopt.erc1155slot import erc1155slot 
from ethopt.lbethwallet import lbethwallet

import web3
from web3 import Web3

#module name
name="ethproxy"

ERC20_NAME      = "erc20"
ERC1155_NAME    = "erc1155"
ERC721_NAME     = "erc721"

contract_codes = {
        ERC20_NAME      : {"abi":erc20_std_abi.ABI, "bytecode":erc20_std_abi.BYTECODE, "token_type": "erc20"},
        ERC1155_NAME    : {"abi":erc1155_std_abi.ABI, "bytecode":erc1155_std_abi.BYTECODE, "token_type": "erc1155"},
        }

class walletproxy(lbethwallet):
    @classmethod
    def load(self, filename):
        ret = self.recover(filename)
        return ret

    @classmethod
    def loads(self, data):
        ret = self.recover_from_mnemonic(data)
        return ret

    def find_account_by_address_hex(self, address):
        for i in range(self.child_count):
            if self.accounts[i].address == address:
                return (i, self.accounts[i])

        return (-1, None)

    @classmethod
    def is_valid_address(self, address):
        return Web3.isAddress(address)

    def __getattr__(self, name):
        if name.startswith('__') and name.endswith('__'):
            raise AttributeError

class ethproxy():

    def clientname(self):
        return name
    
    def __init__(self, host, port, usd_chain = True, *args, **kwargs):
        self._w3 = None
        self.tokens_address = {}
        self.tokens_decimals = {}
        self.tokens = {}
        self.tokens_id = []
        self.__usd_chain_contract_info = usd_chain

        self.connect(host, port, *args, **kwargs)

    def connect(self, host, port = None, *args, **kwargs):
        url = host
        if "://" not in host:
            url = f"http://{host}"
            if port is not None:
                url += f":{port}"

        self._w3 = Web3(Web3.HTTPProvider(url))

    def __get_contract_info(self, name, tokentype = ERC20_NAME):
        contract = contract_codes.get(name)
        assert contract is not None, f"contract name({name}) is invalid."
        return contract

    def local_contract_info(self):
        json_print(contract_codes)

    def load_contract(self, name, address, tokentype = ERC20_NAME):
        contract = self.__get_contract_info(name)
        assert contract is not None, f"not support token({name})"
        erc_token = None
        if name == ERC20_NAME:
            erc_token = erc20slot(self._w3.eth.contract(Web3.toChecksumAddress(address), abi=contract["abi"]))
            self.tokens_decimals[name] = pow(10, self.__get_token_decimals_with_name(erc_token, name))
        else:
            erc_token = erc1155slot(self._w3.eth.contract(Web3.toChecksumAddress(address), abi=contract["abi"]))
            self.tokens_decimals[name] = 0

        setattr(self, name, erc_token)

        self.tokens_address[name] = address
        self.tokens[name] = erc_token 
        self.tokens_id.append(name)

    def token_address(self, name):
        return self.tokens_address[name]

    def is_connected(self):
        return self._w3.isConnected()
    
    def syncing_state(self):
        return self._w3.eth.syncing

    def get_decimals(self, token):
        return self.tokens_decimals[token]

    def allowance(self, owner, spender, token_id, **kwargs):
        return self.tokens[token_id].allowance(owner, spender)

    def approve(self, account, spender, amount, token_id, timeout = 180, **kwargs):
        calldata = self.tokens[token_id].raw_approve(spender, amount)
        return self.send_contract_transaction(account.address, account.key, calldata, timeout = timeout) 

    def send_token(self, account, to_address, amount, token_id, nonce = None, timeout = 180, id = None):
        if token_id.lower() == "eth":
            return self.send_eth_transaction(account.address, account.key, to_address, amount, nonce = nonce, timeout = timeout) 
        else:
            calldata = None
            if self.tokens[token_id].slot_name == ERC20_NAME:
                calldata = self.tokens[token_id].raw_transfer(to_address, amount)
            elif self.tokens[token_id].slot_name == ERC1155_NAME:
                calldata = self.tokens[token_id].raw_transfer_from(accoun.address, to_address, id, amount)
            else:
                raise Exception("token_id[{}] is not [{}]".format(token_id, self.tokens_id))

            return self.send_contract_transaction(account.address, account.key, calldata, nonce = nonce, timeout = timeout) 

    def get_txn_args(self, sender, nonce = None, gas = None, gas_price = None, calldata = None):
        if not gas_price:
            gas_price = self._w3.eth.gasPrice

        if not nonce:
            nonce = self._w3.eth.getTransactionCount(Web3.toChecksumAddress(sender))

        if not gas:
            if calldata:
                gas = calldata.estimateGas({"from":sender})
            else:
                gas = self._w3.eth.estimateGas({"from":sender})

        return (nonce, gas, gas_price)

    def send_eth_transaction(self, sender, private_key, to_address, amount, nonce = None, gas = None, gas_price = None, timeout = 180):
        nonce, gas, gas_price = self.get_txn_args(sender, nonce, gas, gas_price)
        signed_txn = self._w3.eth.account.sign_transaction(dict(
            chainId = self.get_chain_id(),
            nonce = nonce,
            to = to_address,
            value = amount,
            gas = gas,
            gasPrice = gas_price
            ),
            private_key=private_key 
            )

        return self.send_transaction(signed_txn, timeout)

    def send_contract_transaction(self, sender, private_key, calldata, nonce = None, gas = None, gas_price = None, timeout = 180):
        nonce, gas, gas_price = self.get_txn_args(sender, nonce, gas, gas_price, calldata)
        raw_tran = calldata.buildTransaction({
            "chainId": self.get_chain_id(),
            "gas" : gas,
            "gasPrice": gas_price,
            "nonce" : nonce
            })

        signed_txn = self._w3.eth.account.sign_transaction(raw_tran, private_key=private_key)
        return self.send_transaction(signed_txn, timeout)

    def send_transaction(self, signed_txn, timeout):
        txhash = self._w3.eth.sendRawTransaction(signed_txn.rawTransaction)

        #wait transaction, max time is 120s
        self._w3.eth.waitForTransactionReceipt(txhash, timeout)
        return self._w3.toHex(txhash)

    def call_default(self, *args, **kwargs):
        print(f"no defined function(args = {args} kwargs = {kwargs})")

    def block_number(self):
        return self._w3.eth.blockNumber

    def get_balance(self, address, token_id, *args, **kwargs):
        if token_id == "eth":
            return self._w3.eth.getBalance(address)
        return self.tokens[token_id].balance_of(address, kwargs)

    def get_balances(self, address, *args, **kwargs):
        balances = {}
        for token_id in self.tokens_id:
            id = kwargs.get("id")
            balances.update({"{}{}".format(token_id, "_" + id if id else ""): 
                self.get_balance(address, token_id, kwargs)})

        return balances

    def get_rawtransaction(self, txhash):
        return self._w3.eth.getTransaction(txhash)

    def get_chain_id(self):
        return self._w3.eth.chainId

    def uri(self, token_id):
        return self.tokens[token_id].uri()

    def __getattr__(self, name):
        if name.startswith('__') and name.endswith('__'):
            # Python internal stuff
            raise AttributeError
        raise Exception(f"not defined function:{name}")
        
    def __call__(self, *args, **kwargs):
        pass


def main():
    client = clientproxy.connect("")
    client.local_contract_info();
if __name__ == "__main__":
    main()
