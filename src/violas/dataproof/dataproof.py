#!/usr/bin/python3
import sys, getopt, os
import json
import asyncio
sys.path.append("..")

DATAS_ROOT_PATH = "datas_root_path"
DATAS_DB_PATH   = "datas_db_path"
_default_value  = {}
class dataproof():
    ADDRS_SPLIT = ","
    FIELD_SPLIT = ":"

    def __init__(self):
        pass

    def set_default_value(self, key, value):
        _default_value.update({key:value})

    def get_default_value(self, key):
        return _default_value.get(key)

    def get_config(self, key):
        return self.get_default_value(key)

    def set_config(self, key, value):
        self.set_default_value(key, value)

    def default_values(self):
        return _default_value

    @property
    def datas(self):
        datas = {}
        datas.update(_default_value)
        return datas

class walletdatas(dataproof):
    def __init__(self):
        dataproof.__init__(self)
        self.__init_defalut()

    def __init_defalut(self):
        self.__init_wallet_info()

    def __wallet_key(self, chain):
        return f"{chain}_wallet"

    def __init_wallet_info(self):
        self.set_default_value(f"{self.__wallet_key('ethereum')}", "ewallet")

    def get_wallet(self):
        key = self.__wallet_key('ethereum')
        return self.get_config(key)

    def update_wallet(self, chain, data):
        key = self.__wallet_key(chain)
        return self.set_config(key, data)

    def __call__(self, *args, **kwargs):
        return self.get_wallet(args[0])


class configdatas(dataproof):
    def __init__(self):
        dataproof.__init__(self)
        self.__init_default()

    def __init_default(self):
        pass

    def __getattr__(self, name):
        pass

    def __call__(self, *args, **kwargs):
        key = args[0]
        return self.get_config(key)


wallets = walletdatas()
configs = configdatas()

if __name__ == "__main__":
    print(wallets("violas"))
    print(configs("violas_wallet"))
    print(setting.setting.get_conf_env())
