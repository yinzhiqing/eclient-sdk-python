import json
import sys
import os
import typing

abi_files = {
        "nft1155": "./ViolasNft1155.json",
        "nft721": "./ViolasNft721.json"
        }
contract_conf_files = "vlscontract.json"

MOUDLE  = typing.Literal["nft721", "nft1155"]

FIX_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "./jsons")

def get_abspath(filename):
    return os.path.join(FIX_PATH, filename);

def load_abi_address(module : MOUDLE):
    conf_file = get_abspath(contract_conf_files)
    abis_file = get_abspath(abi_files[module]);

    if not os.path.exists(conf_file):
        raise FileExistsError(f"{conf_file} not found.")

    if not os.path.exists(abis_file):
        raise FileExistsError(f"{abis_file} not found.")

    abi_data = ""
    with open(abis_file, "r") as fs:
        confs   = json.load(fs)
        abi_data = confs["abi"]
    
    with open(conf_file, "r") as fs:
        confs   = json.load(fs)
        address = confs[module]["address"]

    return (abi_data, address)
