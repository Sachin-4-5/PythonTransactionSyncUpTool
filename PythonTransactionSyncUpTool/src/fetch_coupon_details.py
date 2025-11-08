import json
import math
import requests
import pandas as pd
from datetime import date, datetime
from requests.auth import HTTPBasicAuth
from concurrent.futures import ThreadPoolExecutor, as_completed
from logging import getLogger, CRITICAL

pd.set_option('display.max_rows', None)


class CouponAPI:
    
    def __init__(self, url, token, user, pwd, log):
        self.log=log
        self.url=url
        self.token=token
        self.user=user
        self.pwd=pwd
        self.request_id=12345678910
        self.log.debug(f'initialized coupon api {user}@{url}')



    # Batch processing + Concurrency (parallel execution)
    def fetch_coupon_details_batch(self, securityIDList):
        all_securityIDs = []
        batch_size = 50
        securityID_batch_list = [securityIDList[i:i + batch_size] for i in range(0, len(securityIDList), batch_size)]

        # Fetch security details for each batch concurrently
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(self.fetch_coupon_details_all, securities, 'BOND')
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



    def fetch_coupon_details_all(self, securityList:list, bondClass='BOND'):
        coupon_data = []
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
            'bondIdType':bondClass
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
            data = response.json()
            as_of_dt = datetime.today().date()
            coupon_details = data.get('couponDataByAssetId', {})
            if not coupon_details:
                self.log.info(f"No coupon data found for securities: {securityIDList}. Skipping...")
                return []
            
            for security_key, coupon_detail in coupon_details.items():
                coupon_record = coupon_detail.get('couponEffectiveDate', {})
                if not coupon_record:
                    self.log.info(f"No coupon effective date for securities: {securityIDList}. Skipping...")
                    continue

                latest_record = None
                latest_date = None
                for coupon_record_key, coupon_record_details in coupon_detail.items():
                    if coupon_record_key=='assetId' or type(coupon_record_details) is str:
                        continue

                    # logic to fetch most recent coupon EffectiveDate <= Todays_Date per assetId
                    effective_dt = datetime.strptime(coupon_record_key, "%Y-%m-%d").date()
                    if effective_dt <= as_of_dt:
                        if latest_date is None or effective_dt > latest_date:
                            latest_date = effective_dt
                            latest_record = coupon_record_details

                if latest_record:
                    coupon_data.append({
                        "bondId": securityIDList,
                        "rate": latest_record.get('cpn', 0),
                        "EffectiveDate": latest_record.get('EffectiveDate'),
                        "cpnSource": latest_record.get('cpnSource', '')
                    })
            return coupon_data    # List of tuples

        except Exception as e:
            self.log.error(f"Mapping error for {securityIDList}: {str(e)} %s")
            raise SystemExit(-1) 
