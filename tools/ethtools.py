#!/usr/bin/python3
import time
import operator
import sys, getopt
import json
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))

import traceback
import datetime
import web3
from web3 import Web3
from enum import Enum

from src.violas import *
#module name
name="ethtools"
chain = "ethereum"

TOKEN_DEF_1155 = "erc1155"
TOKEN_DEF_721 = "erc721"

token_id = TOKEN_DEF_1155
#load logging
logger = log.logger.getLogger(name) 

wallet = None

def setup():
    global wallet
    global client
    wallet = get_ethwallet()
    client = get_ethclient()

def run(argc, argv, exit = True):
    global token_id 
    try:
        logger.debug("start eth.main")
        pargs = parseargs(exit = exit)
        init_args(pargs)
        if pargs.show_help(argv):
            return

        opts, err_args = pargs.getopt(argv)
    except getopt.GetoptError as e:
        logger.error(e)
        if exit:
            sys.exit(2)
        return 
    except Exception as e:
        logger.error(e)
        if exit:
            sys.exit(2)
        return 

    #argument start for --
    if len(err_args) > 0:
        pargs.show_args()
        return

    names = [opt for opt, arg in opts]
    pargs.check_unique(names)

    for opt, arg in opts:
        arg_list = []
        if len(arg) > 0:
            count, arg_list = pargs.split_arg(opt, arg)

            print("opt = {}, arg = {}".format(opt, arg_list))
        if pargs.is_matched(opt, ["help"]):
            pargs.show_args()
            return
        elif pargs.is_matched(opt, ["tokenid"]):
            logger.debug("..................")
            token_id = arg
        elif pargs.is_matched(opt, ["wallet"]):
            if not arg:
                pargs.exit_error_opt(opt)

            global eth_wallet
            global ewclient
            global wallet
            ewclient = None
            eth_wallet = arg
            wallet = get_ethwallet();
        elif pargs.has_callback(opt):
            setup()
            pargs.callback(opt, *arg_list)
        else:
            raise Exception(f"not found matched opt{opt}")
    logger.debug("end manage.main")

'''
*************************************************main oper*******************************************************
'''
def init_args(pargs):
    pargs.clear()
    pargs.append("help", "show arg list.")
    pargs.append("wallet", "inpurt wallet file or mnemonic", True, "file name/mnemonic", priority = 13, argtype = parseargs.argtype.STR)
    pargs.append("tokenid", "set tokenid(erc1155 erc721. default: erc1155)", True, "erc type", priority = 13, argtype = parseargs.argtype.STR)

    #wallet 
    pargs.append(new_wallet, "new wallet.")
    pargs.append(new_account, "new account and save to local wallet.")
    pargs.append(account, "show account info.")
    pargs.append(has_account, "has target account in wallet.")
    pargs.append(accounts, "show all counts address list(local wallet).")
    pargs.append(accounts_full, "show all counts address list(local wallet) with privkey.")

    #client
    pargs.append(send_coin_erc20, "send token(erc20 coin) to target address")
    pargs.append(send_coin_erc1155, "send token(erc1155 coin) to target address")
    pargs.append(approve, "approve to_address use coin amount from from_address")
    pargs.append(allowance, "request to_address can use coin amount from from_address")
    pargs.append(balance, "get address's token(module) amount.")
    pargs.append(balances, "get address's tokens.")
    pargs.append(rawtransaction, "get transaction from eth nodes.")
    pargs.append(syncing_state, "get chain syncing state.",)
    pargs.append(mint, "mint id of token_id.")
    pargs.append(mint_721, "mint token of erc721.")
    pargs.append(token_fields, "show id field info of token_id.")
    pargs.append(token_ids_count, "show count of token.")
    pargs.append(token_ids, "show part of tokens.")
    pargs.append(type_count, "show count of type.")
    pargs.append(type_list, "show type list.")
    pargs.append(append_type, "new type.")
    pargs.append(token_list, "show all token.")
    pargs.append(sha3_id, "make id(sha3).")
    pargs.append(sha3_id_rand, "make rand id(sha3).")
    
    #pargs.appends(globals(), 
    #        no_includes = [run, 
    #            init_args])

'''
*************************************************ethwallet oper*******************************************************
'''

def new_wallet(wallet_name):
    ewclient = ethwallet(name, wallet_name, chain)

def new_account():
    ret = wallet.new_account()
    wallet.dump_wallet()
    assert ret.state == error.SUCCEED, "new_account failed"
    logger.debug("account address : {}".format(ret.datas.address))

def accounts():
    i = 0
    account_count = wallet.get_account_count()
    print(f"account count: {account_count}")
    while True and i < account_count:
        ret = wallet.get_account(int(i))
        if ret.state != error.SUCCEED:
            break 
        account = ret.datas
        logger.debug(f"{i}: {account.address}")
        i += 1

def accounts_full():
    i = 0
    account_count = wallet.get_account_count()
    while True and i < account_count:
        ret = wallet.get_account(i)
        if ret.state != error.SUCCEED:
           break 
        account = ret.datas
        logger.debug(f"({i:03}): address: {account.address} privkey: {account.key.hex()}")
        i += 1

def account(address):
    print(client.get_account_state(address).datas)

def has_account(address):
    logger.debug(wallet.has_account_by_address(address).datas)

'''
*************************************************ethclient oper*******************************************************
'''

client = None
eth_nodes   = [dict(
    host  = "http://124.251.110.238/rpc",
    name  = "violins",
    )]
eth_wallet  = "ewallet"
eth_tokens = dict(
        erc1155 = dict(address='', tokentype=ERC1155_NAME)
        )
def get_ethclient():
    global client
    if client:
        return client
    client = ethclient(name, eth_nodes, chain)
    client.load_contract(token_id, tokentype=token_id)
    return client
    
ewclient = None
def get_ethwallet():
    global ewclient
    if ewclient:
        return eclient
    ewclient = ethwallet(name, eth_wallet, chain)
    return ewclient

def get_ethproof(dtype = "v2b"):

    return requestclient(name, "")

def send_coin_erc20(from_address, to_address, amount, token_id):
    ret = wallet.get_account(from_address)
    if ret.state != error.SUCCEED:
        raise Exception("get account failed")
    account = ret.datas

    ret = client.send_coin_erc20(account, to_address, amount, token_id)
    assert ret.state == error.SUCCEED, ret.message
    print(f"cur balance :{client.get_balance(account.address, token_id).datas}")

def send_coin_erc1155(from_address, to_address, amount, token_id, id):
    ret = wallet.get_account(from_address)
    if ret.state != error.SUCCEED:
        raise Exception("get account failed")
    account = ret.datas

    ret = client.send_coin_erc1155(account, to_address, amount, token_id, id)
    assert ret.state == error.SUCCEED, ret.message
    print(f"cur balance :{client.get_balance(account.address, token_id, id = id).datas}")

def mint(manager, to_address, id, amount, data = None):
    ret = wallet.get_account(manager)
    if ret.state != error.SUCCEED:
        raise Exception("get account failed")
    account = ret.datas

    ret = client.mint(account, token_id, to_address, id, amount, data)
    assert ret.state == error.SUCCEED, ret.message
    print(f"cur balance :{client.get_balance(account.address, token_id, id = id).datas}")

def mint_721(manager, to_address, id, tid):
    ret = wallet.get_account(manager)
    if ret.state != error.SUCCEED:
        raise Exception("get account failed")
    account = ret.datas

    ret = client.mint(account, token_id, to_address, id, 1, None, tid = tid)
    assert ret.state == error.SUCCEED, ret.message
    print(f"cur balance :{client.get_balances(account.address).datas}")

def exchange_blind_box(manager, to_address, id, data = None):
    ret = wallet.get_account(manager)
    if ret.state != error.SUCCEED:
        raise Exception("get account failed")
    account = ret.datas

    ret = client.exchange_blind_box(account, token_id, to_address, id, data)
    assert ret.state == error.SUCCEED, ret.message
    print(f"cur balance :{client.get_balance(account.address, token_id, id = id).datas}")

def approve(from_address, to_address, amount, token_id):
    ret = wallet.get_account(from_address)
    if ret.state != error.SUCCEED:
        raise Exception("get account failed")
    account = ret.datas

    ret = client.approve(account, to_address, amount, token_id)
    assert ret.state == error.SUCCEED, ret.message
    print(f"cur balance :{client.allowance(from_address, to_address, token_id).datas}")

def allowance(from_address, to_address, token_id):
    ret = client.allowance(from_address, to_address, token_id)
    assert ret.state == error.SUCCEED, ret.message
    print(f"allowance balance :{ret.datas}")

def balance(address, token_id, id = None):
    logger.debug(f"start balance address= {address} token_id= {token_id}, id = {id}")
    ret = client.get_balance(address, token_id, id = id)
    logger.debug("balance: {0}".format(ret.datas))

def decimals(token_id):
    logger.debug(f"start decimals token_id= {token_id}")
    ret = client.get_decimals(token_id)
    logger.debug(f"decimals: {ret}")

def balances(address):
    logger.debug(f"start balances address= {address}")
    ret = client.get_balances(address)
    logger.debug("balance: {0}".format(ret.datas))


def rawtransaction(txhash):
    logger.debug(f"start rawtransaction(txhash={txhash}")

    ret = client.get_rawtransaction(txhash)
    if ret.state != error.SUCCEED:
        return

    print(ret.datas)

def syncing_state():
    logger.debug(f"start syncing_state()")
    ret = client.get_syncing_state()
    logger.debug("syncing state: {0}".format(ret.datas))

def chain_id():
    logger.debug(f"start chain_id()")
    ret = client.get_chain_id()
    logger.debug("chain id: {0}".format(ret.datas))

def token_id_address():
    logger.debug("start token_id_address({})".format(token_id))
    ret = client.get_token_id_address(token_id)
    logger.debug("address: {0}".format(ret.datas))

def token_id_uri():
    logger.debug("start token_id_address({})".format(token_id))
    ret = client.get_token_id_uri(token_id)
    logger.debug("address: {0}".format(ret.datas))

def token_ids_count():
    logger.debug("start token_ids_count({})".format(token_id))
    ret = client.get_token_ids_count(token_id)
    logger.debug("totle ids count: {0}".format(ret.datas))

def token_ids(start = 0, limit = 10):
    logger.debug("start token_ids({}, {}, {})".format(start, limit, token_id))
    ret = client.get_token_ids(token_id, start = start, limit = limit)
    logger.debug("totle ids: ".format(ret.datas))
    json_print(ret.datas)

def token_fields(id):
    logger.debug("start token_fields({})".format(token_id))
    ret = client.get_token_fields(token_id,id)
    logger.debug("address: {0}".format(ret.datas))

def token_id_total_amount(id):
    logger.debug("start token_id_total_amount({}, {})".format(token_id, id))
    ret = client.get_token_id_total_amount(token_id, id)
    logger.debug("totle amount: {0}".format(ret.datas))

def type_count():
    logger.debug("start type_count({})".format(token_id))
    ret = client.type_count(token_id)
    logger.debug("type_count: {0}".format(ret.datas))

def __assert_result(ret, msg = ""):
    assert ret.state == error.SUCCEED, "{}:{}".format(msg, ret.message)

def __show_filed_list(call_count, call_name, fixed_start = True, fixed_value = 0):
    ret = call_count(token_id)
    __assert_result(ret)

    logger.debug("count: {}".format(ret.datas))
    logger.debug("-" * 20)

    start = fixed_value
    if not fixed_start:
        start = client.index_start(token_id) 

    logger.debug("start: {}".format(start))
    for id in range(ret.datas):
        ret = call_name(token_id, id + start)
        __assert_result(ret)
        logger.debug("index: {}\t|\tdata: {}".format(id + start, ret.datas))

def token_list():
    __show_filed_list(client.get_token_ids_count, client.token_id, -1)

def brand_list():
    __show_filed_list(client.brand_count, client.brand_name)

def type_list():
    __show_filed_list(client.type_count, client.type_name)

def quality_list():
    __show_filed_list(client.quality_count, client.quality_name)

def nfttype_list():
    __show_filed_list(client.nfttype_count, client.nfttype_name)

def nfttype_type():
    ret = client.nfttype_count(token_id)
    __assert_result(ret)

    logger.debug("count: {}".format(ret.datas))
    logger.debug("-" * 20)
    logger.debug("id \t |  name \t | type")
    for id in range(ret.datas):
        ret = client.nfttype_name(token_id, id + 1)
        __assert_result(ret)
        name = ret.datas
        ret = client.is_blind_box(token_id, id + 1)
        __assert_result(ret)
        if ret.datas:
            logger.debug("{} \t | {} \t | {}".format(id + 1, name, "blindbox"))
            continue

        ret = client.is_exchange(token_id, id + 1)
        __assert_result(ret)
        if ret.datas:
            logger.debug("{} \t | {} \t | {}".format(id + 1, name, "exchange"))
            continue

        logger.debug("{} \t | {} \t | {}".format(id + 1, name, "normal"))

def mint_brand(manager, to, brand, data = None):
    ret = wallet.get_account(manager)
    if ret.state != error.SUCCEED:
        raise Exception("get account failed")
    account = ret.datas

    ret = client.mint_brand(account, token_id, to, brand, data)
    __assert_result(ret)
    logger.debug(ret.datas)

def mint_type(manager, to, brand, btype, data = None):
    ret = wallet.get_account(manager)
    if ret.state != error.SUCCEED:
        raise Exception("get account failed")
    account = ret.datas

    ret = client.mint_type(account, token_id, to, brand, btype, data)
    __assert_result(ret)
    logger.debug(ret.datas)

def append_type(manager, capacity, data):
    ret = wallet.get_account(manager)
    if ret.state != error.SUCCEED:
        raise Exception("get account failed")
    account = ret.datas

    id = client.sha3_id(num = data).datas
    ret = client.append_type(account, token_id, id, capacity, data)
    __assert_result(ret)
    logger.debug(ret.datas)



def mint_quality(manager, to, brand, btype, quality, nfttype = "normal", data = None):
    ret = wallet.get_account(manager)
    if ret.state != error.SUCCEED:
        raise Exception("get account failed")
    account = ret.datas

    ret = client.mint_quality(account, token_id, to, brand, btype, quality, nfttype, data)
    __assert_result(ret)
    logger.debug(ret.datas)

def mint_sub_token(manager, to, quality_id, amount, data = None, timeout = 180):
    ret = wallet.get_account(manager)
    if ret.state != error.SUCCEED:
        raise Exception("get account failed")
    account = ret.datas

    ret = client.mint_sub_token(account, token_id, to, quality_id, amount, data)
    __assert_result(ret)
    logger.debug(ret.datas)

def sha3_id(data):
    sid = client.sha3_id(text = data).datas
    logger.debug("sid: {}".format(sid))

def sha3_id_rand():
    data = "{}".format(int(time.time()))
    logger.debug("metadata: {}".format(data))
    sid = client.sha3_id(num = data).datas
    logger.debug("sid: {}".format(sid))

def test():
    sid = client.sha3_id("0x03").datas
    logger.debug("sid: {}".format(sid))










if __name__ == "__main__":
    run(len(sys.argv) - 1, sys.argv[1:])
    #test()
