
# This file is use to fetch API details like (token, user key, passwords) and connection string from another static application
# For example - SMSPasswordRetrieval
# Created and stored at another location whose path is present in config.ini


import subprocess
from logging import getLogger, CRITICAL

class SMS():

    def __init__(self, exe_path, log):
        self.exe_path=exe_path
        self.log=log
        self.secrets={}


    def get(self, key):
        if key in self.secrets:
            pass
        else:
            pass
            try:
                self.secrets[key] = self.get_sms_value(key)
            except Exception as e:
                self.log.exception(e)
        return self.secrets.get(key)
    

    def get_sms_value(self, key):
        command = [self.exe_path, key]
        self.log.debug(f"command: {command}")
        self.log.debug(f"executable path: {self.exe_path}")
        try:
            result=subprocess.run(command, capture_output=True, text=True, timeout=3000)
            self.log.debug(f"STOUT: {result.stderr}")
            if result.returncode != 0 or not any(result.stdout) or any(result.stderr):
                raise Exception(f"Error retrieving SMS key '{key}'\n{result}")
            return result.stdout.strip()
        except subprocess.TimeoutExpired:
            self.log.error(f"Timout while retrieving SMS {key}")
            return None