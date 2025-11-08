# This file contains logic for fetching /secueity related details (like-password, api_key, etc) from some external app
# For ex - SMSPassowrdRetreival (console based application returns values on passing keys)

from configparser import ConfigParser
from sys import argv
from os.path import join, dirname, realpath
from sms import SMS
from log_handler import init_log
log = init_log


def mapd(d, fk=lambda k, _: k, fv=lambda _, v: v):
    return {
        fk(k,v): mapd(v, fk, fv) if isinstance(v, dict) else fv(k,v)
        for k, v in d.items()
    }


def read_cfg(log, ini_path=None):
    ini_path = ini_path or join(dirname(realpath(argv[0])), 'config.ini')
    print(f"reading {ini_path}")
    log.info(f'rading {ini_path}')
    config = ConfigParser()
    config.read(ini_path)

    sms = SMS(config.get('sms', 'exe_path'), log)

    def map_key(k, _):
        k=k.lower()
        if k.endswith('_key'):
            k=k[:-4]
        return k
    
    def map_value(k,v):
        if k.lower().emdswith('_key'):
            return sms.get(v)
        else:
            for c in [float, int, eval]:
                try:
                    if str(c(v)) == v: return c(v)
                except:
                    pass
        return v
    return mapd(config.__dict__['_section'], map_key, map_value)