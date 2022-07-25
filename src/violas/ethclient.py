#!/usr/bin/python3
import operator
import sys
import json
import os
sys.path.append(os.getcwd())
sys.path.append("{}".format(os.getcwd()))
sys.path.append("..")
from .log import logger
import traceback
import datetime
from .comm import *
from .ethproxy import (
        ethproxy as clientproxy,
        walletproxy,
        contract_codes,
        ERC20_NAME,
        ERC721_NAME,
        ERC1155_NAME
        )
from enum import Enum
from baseobject import baseobject
#import redis

import web3
from web3 import Web3
from comm.values import (
        ETH_ADDRESS_LEN
        )
#module name
name="eclient"


class ethwallet(baseobject):
    
    def __init__(self, name, wallet, chain="ethereum", main_address = None):
        assert wallet is not None, "wallet is None"
        baseobject.__init__(self, name)
        self.__wallet = None

        if wallet is not None:
            ret = self.__load_wallet(wallet, chain)
            if ret.state != error.SUCCEED:
                raise Exception(f"load wallet[{wallet}] failed.")

    def __del__(self):
        pass

    def __load_wallet(self, wallet, chain="ethereum"):
        try:
            self.__wallet_name = wallet

            if os.path.isfile(wallet):
                self.__wallet = walletproxy.load(wallet)
                ret = result(error.SUCCEED, "", "")
            elif is_mnemonic(wallet):
                self.__wallet_name = None
                self.__wallet = walletproxy.loads(wallet)
                ret = result(error.SUCCEED, "", "")
            else:
                ret = result(error.SUCCEED, "not found wallet file", "")
                #raise Exception(f"not found {self.name()} wallet file({wallet})")
                self.__wallet = walletproxy.new()
                self.save()

        except Exception as e:
            ret = parse_except(e)
        return ret

    def save(self):
        try:
            if self.__wallet is not None and self.__wallet_name:
                self.__wallet.write_recovery(self.__wallet_name)
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def dump_wallet(self):
        try:
            if self.__wallet is not None:
                self.save()
                self.__wallet = None
                pass
            ret = result(error.SUCCEED)
        except Exception as e:
            ret = parse_except(e)
        return ret

    @classmethod
    def is_valid_address(self, address):
        try:
            ret = result(error.SUCCEED, datas = walletproxy.is_valid_address(address))
        except Exception as e:
            ret = parse_except(e)
        return ret

    def new_account(self):
        try:
            account = self.__wallet.new_account();
            self.save()
            ret = result(error.SUCCEED, "", account)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_account_count(self):
        return len(self.__wallet.accounts)

    def get_account(self, addressorid):
        try:
            account = self.__wallet.get_account_by_address_or_refid(addressorid)
            if account is None:
                ret = result(error.ARG_INVALID)
            else:
                ret = result(error.SUCCEED, "", account)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def find_account_by_address_hex(self, address):
        return self.__wallet.find_account_by_address_hex(address)

    def has_account_by_address(self, address):
        try:
            _, account = self.find_account_by_address_hex(address)
            if account is None:
                ret = result(error.SUCCEED, "", False)
            else:
                ret = result(error.SUCCEED, "", True)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def has_account(self):
        try:
            self.__wallet.get_account_by_address_or_refid(0)
            ret = result(error.SUCCEED, "", True)
        except ValueError as e: #account count is 0, so not found account
            ret = result(error.SUCCEED, "", False)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def split_full_address(self, address, auth_key_prefix = None):
        try:
            ret = result(error.SUCCEED, datas = (None, address))
        except Exception as e:
            ret = parse_except(e)
        return ret

    def __getattr__(self, name):
        if name.startswith('__') and name.endswith('__'):
            # Python internal stuff
            raise AttributeError

class ethclient(baseobject):
    def __init__(self, name, nodes, chain = "ethereum", usd_chain = True):
        baseobject.__init__(self, name, chain)
        self.__client = None
        self.__node = None
        if nodes is not None:
            ret = self.conn_node(name, nodes, chain, usd_chain = usd_chain)
            if ret.state != error.SUCCEED:
                raise Exception(f"connect {chain} node failed.")

    def __del__(self):
        self.disconn_node()

    def clientname(self):
        return self.__client.clientname()

    def load_contract(self, token_id, address = None, tokentype = ERC1155_NAME):
        self.__client.load_contract(token_id, address, tokentype)

    def set_contract_map_account(self, account):
        self._sender_map_account = account

    def map_account(self, account):
        return account

    def conn_node(self, name, nodes, chain = "ethereum", usd_chain = False):
        try:
            if nodes is None or len(nodes) == 0:
                return result(error.ARG_INVALID, repr(nodes), "")
            

            for node in nodes:
                try:
                    if self.work() == False:
                        return result(error.FAILED, f"connect {chain} work stop")

                    self._logger.debug("try connect node({}) : host = {} port = {} chain_id = {}".format( \
                            node.get("name", ""), node.get("host"), node.get("port"), node.get("chain_id", 42)))
                    client = clientproxy(host=node.get("host"), \
                            port=node.get("port"), \
                            usd_chain = usd_chain
                            )
                    #if not client.is_connected():
                    #    self._logger.info(f"connect {chain} node failed({e}). test next...")
                    #    continue

                    self._logger.debug(f"connect {chain} node succeed.") 
                except Exception as e:
                    parse_except(e)
                    self._logger.info(f"connect {chain} node failed({e}). test next...")
                else:
                    self.__client = client
                    self.__node = node
                    return result(error.SUCCEED, "", "")

            #not connect any violas node
            ret = result(error.FAILED,  f"connect {chain} node failed.", "")
        except Exception as e:
            ret = parse_except(e)
        return ret
    
    def stop(self):
        self.work_stop()

    def disconn_node(self):
        try:
            ret = result(error.SUCCEED) 
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_syncing_state(self): 
        try:
            ret = result(error.SUCCEED, datas = self.__client.syncing_state()) 
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_balance(self, account_address, token_id, id = None):
        try:
            balance = self.__client.get_balance(account_address, token_id, id = id)
            ret = result(error.SUCCEED, "", balance)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_balances(self, account_address, id = None):
        try:
            balance = self.__client.get_balances(account_address, id = id)
            ret = result(error.SUCCEED, "", balance)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def address_is_exists(self, address):
        try:
            state = self.__client.account_is_exists(address)
            ret = result(error.SUCCEED, "", state)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_rawtransaction(self, txhash):
        try:
            datas = self.__client.get_rawtransaction(txhash)
            ret = result(error.SUCCEED, "", datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    #the same to btc/violas get_decimals
    def get_decimals(self, token_id):
        return self.__client.get_decimals(token_id)

    @output_args
    def approve(self, account, to_address, amount, token_id, **kwargs):
        try:
            datas = self.__client.approve(account, to_address, amount, token_id, **kwargs)
            ret = result(error.SUCCEED, datas = datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    @output_args
    def allowance(self, from_address, to_address, token_id, **kwargs):
        try:
            datas = self.__client.allowance(from_address, to_address, token_id, **kwargs)
            ret = result(error.SUCCEED, datas = datas)
        except Exception as e:
            ret = parse_except(e)
        return ret

    def send_coin_erc20(self, account, toaddress, amount, token_id, *args, **kwargs):
        return self.send_coin(account, toaddress, amount, token_id, data= {"type":"erc20", "version": None},*args, **kwargs)

    def send_coin_erc1155(self, account, toaddress, amount, token_id, id, *args, **kwargs):
        return self.send_coin(account, toaddress, amount, token_id, data= {"type":"erc1155", "version": None}, id = id, *args, **kwargs)

    def send_coin(self, account, toaddress, amount, token_id, data, id = None, *args, **kwargs):
        '''change state 
        '''
        try:
            sender_account = self.map_account(account)
            if data["type"] in ("erc20", "erc1155"):
                datas = self.__client.send_token(sender_account, toaddress, amount, token_id, id = id)
            else:
                raise Exception(f"type{type} is invald.")
            ret = result(error.SUCCEED if len(datas) > 0 else error.FAILED, "", datas = datas)
            self._logger.debug(f"result: {ret.datas}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_token_list(self):
        try:
            ret = result(error.SUCCEED, datas = self.__client.token_name_list())
        except Exception as e:
            ret = parse_except(e)
        return ret

    def token_exists(self, token_id, id):
        try:
            ret = result(error.SUCCEED, datas = self.__client.token_exists(token_id, id))
        except Exception as e:
            ret = parse_except(e)
        return ret

    def brand_count(self, token_id):
        try:
            ret = result(error.SUCCEED, datas = self.__client.brand_count(token_id))
        except Exception as e:
            ret = parse_except(e)
        return ret

    def brand_name(self, token_id, id):
        try:
            ret = result(error.SUCCEED, datas = self.__client.brand_name(token_id, id))
        except Exception as e:
            ret = parse_except(e)
        return ret

    def brand_id(self, token_id, name):
        try:
            ret = result(error.SUCCEED, datas = self.__client.brand_id(token_id, name))
        except Exception as e:
            ret = parse_except(e)
        return ret

    def type_count(self, token_id):
        try:
            ret = result(error.SUCCEED, datas = self.__client.type_count(token_id))
        except Exception as e:
            ret = parse_except(e)
        return ret

    def type_name(self, token_id, id):
        try:
            ret = result(error.SUCCEED, datas = self.__client.type_name(token_id, id))
        except Exception as e:
            ret = parse_except(e)
        return ret

    def type_id(self, token_id, name):
        try:
            ret = result(error.SUCCEED, datas = self.__client.type_id(token_id, name))
        except Exception as e:
            ret = parse_except(e)
        return ret

    def quality_count(self, token_id):
        try:
            ret = result(error.SUCCEED, datas = self.__client.quality_count(token_id))
        except Exception as e:
            ret = parse_except(e)
        return ret

    def quality_name(self, token_id, id):
        try:
            ret = result(error.SUCCEED, datas = self.__client.quality_name(token_id, id))
        except Exception as e:
            ret = parse_except(e)
        return ret

    def quality_id(self, token_id, name):
        try:
            ret = result(error.SUCCEED, datas = self.__client.quality_id(token_id, name))
        except Exception as e:
            ret = parse_except(e)
        return ret

    def nfttype_count(self, token_id):
        try:
            ret = result(error.SUCCEED, datas = self.__client.nfttype_count(token_id))
        except Exception as e:
            ret = parse_except(e)
        return ret

    def nfttype_name(self, token_id, id):
        try:
            ret = result(error.SUCCEED, datas = self.__client.nfttype_name(token_id, id))
        except Exception as e:
            ret = parse_except(e)
        return ret

    def nfttype_id(self, token_id, name):
        try:
            ret = result(error.SUCCEED, datas = self.__client.nfttype_id(token_id, name))
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_token_ids_count(self, token_id):
        try:
            ret = result(error.SUCCEED, datas = self.__client.get_token_ids_count(token_id))
        except Exception as e:
            ret = parse_except(e)
        return ret

    def is_blind_box(self, token_id, nfttype : int):
        try:
            ret = result(error.SUCCEED, datas = self.__client.is_blind_box(token_id, nfttype))
        except Exception as e:
            ret = parse_except(e)
        return ret

    def is_exchange(self, token_id, nfttype : int):
        try:
            ret = result(error.SUCCEED, datas = self.__client.is_exchange(token_id, nfttype))
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_token_fields(self, token_id, id):
        try:
            ret = result(error.SUCCEED, datas = self.__client.get_token_fields(token_id, id))
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_token_ids(self, token_id, start = 0, limit = 10):
        try:
            ret = result(error.SUCCEED, datas = self.__client.get_token_ids(token_id, int(start), int(limit)))
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_chain_id(self):
        try:
            ret = result(error.SUCCEED, datas = self.__client.get_chain_id())
        except Exception as e:
            ret = parse_except(e)
        return ret

    def mint(self, account, token_id, to, id, amount, data = None):
        try:
            datas = self.__client.mint(account, token_id, to, id = id, amount = amount, data = data)
            ret = result(error.SUCCEED if len(datas) > 0 else error.FAILED, "", datas = datas)
            self._logger.debug(f"result: {ret.datas}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def exchange_blind_box(self, account, token_id, to, id, data = None):
        try:
            datas = self.__client.exchange_blind_box(account, token_id, to, id = id, data = data)
            ret = result(error.SUCCEED if len(datas) > 0 else error.FAILED, "", datas = datas)
            self._logger.debug(f"result: {ret.datas}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_token_id_address(self, token_id):
        try:
            ret = result(error.SUCCEED, datas = self.__client.token_address(token_id))
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_token_id_uri(self, token_id):
        try:
            ret = result(error.SUCCEED, datas = self.__client.uri(token_id))
        except Exception as e:
            ret = parse_except(e)
        return ret

    def get_token_id_total_amount(self, token_id, id):
        try:
            ret = result(error.SUCCEED, datas = self.__client.get_token_id_total_amount(token_id, id))
        except Exception as e:
            ret = parse_except(e)
        return ret
    
    def mint_brand(self, account, token_id, to, brand, data = None):
        try:
            datas = self.__client.mint_brand(account, token_id, to, brand, data = data)
            ret = result(error.SUCCEED if len(datas) > 0 else error.FAILED, "", datas = datas)
            self._logger.debug(f"result: {ret.datas}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def mint_type(self, account, token_id, to, brand, btype, data = None):
        try:
            datas = self.__client.mint_type(account, token_id, to, brand, btype, data = data)
            ret = result(error.SUCCEED if len(datas) > 0 else error.FAILED, "", datas = datas)
            self._logger.debug(f"result: {ret.datas}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def mint_quality(self, account, token_id, to, brand, btype, quality, nfttype = "", data = None, timeout = 180):
        try:
            datas = self.__client.mint_quality(account, token_id, to, brand, btype, quality, nfttype, data = data)
            ret = result(error.SUCCEED if len(datas) > 0 else error.FAILED, "", datas = datas)
            self._logger.debug(f"result: {ret.datas}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def mint_sub_token(self, account, token_id, to, quality_id, amount, data = None, timeout = 180):
        try:
            datas = self.__client.mint_sub_token(account, token_id, to, quality_id, amount, data = data)
            ret = result(error.SUCCEED if len(datas) > 0 else error.FAILED, "", datas = datas)
            self._logger.debug(f"result: {ret.datas}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def append_blind_box_id(self, account, token_id, nfttype, timeout = 180):
        try:
            datas = self.__client.append_blind_box_id(account, token_id, nfttype)
            ret = result(error.SUCCEED if len(datas) > 0 else error.FAILED, "", datas = datas)
            self._logger.debug(f"result: {ret.datas}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def cancel_blind_box_id(self, account, token_id, nfttype, timeout = 180):
        try:
            datas = self.__client.cancel_blind_box_id(account, token_id, nfttype)
            ret = result(error.SUCCEED if len(datas) > 0 else error.FAILED, "", datas = datas)
            self._logger.debug(f"result: {ret.datas}")
        except Exception as e:
            ret = parse_except(e)
        return ret

    def __getattr__(self, name):
        if name.startswith('__') and name.endswith('__'):
            # Python internal stuff
            raise AttributeError
        return self.__client

#------------------------------------------extend-----------------------------------------------
def main():
    pass
if __name__ == "__main__":
    main()
