#!/usr/bin/python3

import sys, os, time
sys.path.append(os.getcwd())
sys.path.append(f"..")

import web3
from web3 import Web3

class idfields():
    def __init__(self, id):
        self.__parse(id)

    def to_json(self):
        return dict(
                mark    = self.mark,
                version = self.version,
                reserve = self.reserve,
                brand   = self.brand,
                btype   = self.btype,
                quality = self.quality,
                nfttype = self.nfttype,
                quality_index   = self.quality_index,
                subtoken_index  = self.subtoken_index,
                issubtoken      = self.issubtoken,
                parent_token    = self.parent_token,
                id = self.id
                )

    def __parse(self, id):
        id = self.__convert_to_hex(id)
        setattr(self, "id", id)
        setattr(self, "mark", id[0:16])
        setattr(self, "version", id[16:24])
        setattr(self, "reserve", id[24:28])
        setattr(self, "brand", id[28:36])
        setattr(self, "btype", id[36:40])
        setattr(self, "quality", id[40:44])
        setattr(self, "nfttype", id[44:48])
        setattr(self, "quality_index", id[48:56])
        setattr(self, "subtoken_index", id[56:])
        setattr(self, "issubtoken", self.__convert_to_int(id[56:]) > 0)
        setattr(self, "parent_token", self.__parent_token())


    def __parent_token(self):
        mark    = self.mark
        version = self.version
        reserve = self.reserve
        brand   = self.brand
        btype   = self.btype
        quality = self.quality
        nfttype = self.nfttype
        quality_index   = self.quality_index
        subtoken_index  = self.subtoken_index
        issubtoken      = self.issubtoken

        if issubtoken:
            subtoken_index  = ''.join(['0' for i in subtoken_index])
            #临时转换一下 tmp_set
            if self.__convert_to_int(nfttype) == 2:
                nfttype = "0001"
        elif self.__convert_to_int(quality) > 0:
            quality         = ''.join(['0' for i in quality])
            nfttype         = ''.join(['0' for i in nfttype])
            quality_index   = ''.join(['0' for i in quality_index])
        elif self.__convert_to_int(btype) > 0:
            btype           = ''.join(['0' for i in btype])
        else:
            return ""

        return mark + version + reserve + brand + btype + quality + nfttype + quality_index + subtoken_index

    def __convert_to_int(self, value):
        if value and isinstance(value, str):
            value = Web3.toInt(hexstr = value)
        return value

    def __convert_to_hex(self, value):
        if value and not isinstance(value, str):
            value = Web3.toHex(value)
        return value[2:] if value.lower().startswith("0x") else value

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

#*************************************extende********************************************
    def tokenCount(self):
        return self._contract.functions.tokenCount().call()

    def tokenTotalAmount(self, id):
        id = self.__convert_to_int(id)
        return self._contract.functions.tokenTotleAmount(id).call()

    def token_id(self, index):
        return self.__convert_to_hex(self._contract.functions.tokenId(index).call())

    def token_exists(self, id):
        id = self.__convert_to_int(id)
        return self._contract.functions.tokenExists(id).call()

    def brand_count(self):
        return self._contract.functions.brandCount().call()

    def brand_name(self, id):
        id = self.__convert_to_int(id)
        return self._contract.functions.brandName(id).call()

    def brand_id(self, name):
        return self.__convert_to_hex(self._contract.functions.brandId(name).call())

    def type_count(self):
        return self._contract.functions.typeCount().call()

    def type_name(self, id):
        id = self.__convert_to_int(id)
        return self._contract.functions.typeName(id).call()

    def type_id(self, name):
        return self.__convert_to_hex(self._contract.functions.typeId(name).call())

    def quality_count(self):
        return self._contract.functions.qualityCount().call()

    def quality_name(self, id):
        id = self.__convert_to_int(id)
        return self._contract.functions.qualityName(id).call()

    def quality_id(self, name):
        return self.__convert_to_hex(self._contract.functions.qualityId(name).call())

    def nfttype_count(self):
        return self._contract.functions.nftTypeCount().call()

    def nfttype_name(self, id):
        id = self.__convert_to_int(id)
        return self._contract.functions.nftTypeName(id).call()

    def nfttype_id(self, name):
        return self.__convert_to_hex(self._contract.functions.nftTypeId(name).call())

    def is_blind_box(self, nfttype): #nfttype is id
        nfttype = self.__convert_to_int(nfttype)
        return self._contract.functions.isBlindBox(nfttype).call()

    def is_exchange(self, nfttype): #nfttype  is id
        nfttype = self.__convert_to_int(nfttype)
        return self._contract.functions.isExchange(nfttype).call()

    def raw_mint_brand(self, to, brand, data):
        return self._contract.functions.mintBrand(to, brand, data)

    def raw_mint_type(self. to, brand, btype, data):
        return self._contract.functions.mintType(to, brand, btype, data)

    def raw_mint_quality(to, brand, btype, quality, nfttype, data):
        data = b'' if not data else data
        return self._contract.functions.to, brand, btype, quality, nfttype, data)

    def raw_mint_sub_token(to, qualityid, amount, data):
        qualityid = self.__convert_to_int(qualityid)
        amount  = self.__convert_to_int(amount)
        data = b'' if not data else data
        return self._contract.functions.mintSubToken(to, qualityid, amount, data)

    def raw_exchange_blind_box(self, to, id, data = None):
        id      = self.__convert_to_int(id)
        data = b'' if not data else data
        return self._contract.functions.exchangeBlindBox(Web3.toChecksumAddress(to), id, data)

    def raw_append_blind_box_id(self, nfttype): #nfttype = name
        return self._contract.functions.appendBlindBoxId(nfttype)
    
    def raw_cancel_blind_box_id(self, nfttype): # nfttype is name
        return self._contract.functions.cancelBlindBoxId(nfttype)

#*************************************internal********************************************#
    def __convert_to_int(self, value):
        if value and isinstance(value, str):
            value = Web3.toInt(hexstr = value)
        return value

    def __convert_to_hex(self, value):
        if value and not isinstance(value, str):
            value = Web3.toHex(value)
        return value[2:] if value.lower().startswith("0x") else value

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
