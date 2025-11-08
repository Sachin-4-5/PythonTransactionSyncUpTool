import json
import math
import requests
import pandas as pd
from datetime import date, datetime
from requests.auth import HTTPBasicAuth
from concurrent.futures import ThreadPoolExecutor, as_completed
from logging import getLogger, CRITICAL


pd.set_option('Display.max_rows', None)


class SecurityAPI:

    def __init__(self, url, token, user, pwd, log):
        self.log=log
        self.url=url
        self.token=token
        self.user=user
        self.pwd=pwd
        self.request_id=12345678910
        self.log.debug(f'initialized security api {user}@{url}')



    # Batch processing + Concurrency (parallel execution)
    def fetch_security_details_batch(self, securityIDList):
        all_securityIDs = []
        batch_size = 50
        securityID_batch_list = [securityIDList[i:i + batch_size] for i in range(0, len(securityIDList), batch_size)]

        # Fetch security details for each batch concurrently
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(self.fetch_Security_details_all, securities, 'BOND')
                for securities in securityID_batch_list
            ]

            for future in as_completed(futures):
                try:
                    t=future.result()
                    if isinstance(t, list):
                        all_securityIDs += t
                except Exception as e:
                    self.log.error(f"An error occured during concurrent execution of security API: {str(e)} %s", repr(e))
                    raise SystemExit(-1)
                
        return all_securityIDs
    

    # Fetch security details for a list of securities
    def fetch_security_details_all(self, securityList:list, assetClass='BOND'):
        security_data = []
        securityIDList = ""
        for security in securityList:
            if isinstance(security, str):
                securityIDList += security + ","

        headers = {
            'Content-Type':'application/json',
            'Request-ID':str(self.request_id),
            'Origin-Timestamp':datetime.now().isoformat(timespec='milliseconds') + 'Z',
            'API-Key':self.token
        }

        params = {
            'bondId':securityIDList,
            'bondIdType':assetClass
        }

        try:
            response = requests.get(
                self.url,
                headers=headers,
                params=params,
                auth=HTTPBasicAuth(self.user, self.pwd)
            )
            response.raise_for_status()

        except requests.exceptions.RequestException as e:
            self.log.error(f"Request error on {self.url} for {securityIDList}: {str(e)} %s", repr(e))
            raise SystemExit(-1)
        
        try:
            data = response.json
            security_details = data.get('bondByAssetId', {})
            for security_key, security_values in security_details.items():
                for security_record_key, security_record_details in security_values.items():
                    if security_record_key=='bondId' or type(security_record_details) is str:
                        continue
                    bond = security_record_details.get('BOND')
                    fixRate = security_record_details.get('couponFix', 0)
                    floatRate = security_record_details.get('couponFloat', 0)
                    cpnType = security_record_details.get('cpnType', 'F')
                    rate = fixRate if cpnType=='F' else floatRate
                    security_data.append({
                        "bondId": bond,
                        "rate": rate
                    })
            return security_data    # List of tuples

        except Exception as e:
            self.log.error(f"Mapping error for {securityIDList}: {str(e)} %s")
            raise SystemExit(-1) 