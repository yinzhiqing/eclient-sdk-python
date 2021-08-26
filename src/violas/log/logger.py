import logging
import logging.config
from . import config
import os,sys
import threading

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir))
from comm.values import (
        PACKAGE_ROOT_PATH,
        )

lock = threading.Lock()

def __init__():
    print("logger.__init__")

def getLogger(name, path = None):

    lock.acquire()
    log_path = "."
    if path:
        log_path = os.path.abspath(os.path.join(path, "logs"))

    if not os.path.exists(log_path):
        os.makedirs(log_path)

    hfile = dict(config.config["handlers"]["file"])
    hfile["filename"]=f"{log_path}/{name}.log"
    config.config["handlers"].update({name:hfile})
    default = config.config.get("loggers").get("bvelog")
    if name not in config.config.get("loggers"):
        new_logger = dict(default)
        new_logger["handlers"] = ["console", name]
        config.config["loggers"].update({name:new_logger})

    logging.config.dictConfig(config.config)
    logger = logging.getLogger(name)
    lock.release()

    return logger

