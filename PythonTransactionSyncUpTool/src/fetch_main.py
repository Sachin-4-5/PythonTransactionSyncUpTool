
import argparse   # used for parsing the command line arguments.
from datetime import datetime, time, timedelta                  
from concurrent.futures import ThreadPoolExecutor, as_completed # run multiple tasks in parallel (multi-threading).
import pandas as pd   # data analysis library, often for tabular data (like trades).
from dbconnection import DB
from log_handler import init_log
from fetch_security_details import SecurityAPI
from fetch_coupon_details import CouponAPI
from cfg import read_cfg
from cfg_main import read_cfg   # This is getting used


def fetch_main():

    # Step-0: Variable declarations
    print("Start Application")
    log=init_log()
    config=read_cfg(log)
    log.config(**config['log'])
    db = DB(log=log, **config['db'])

    secapi = SecurityAPI(log=log, **config['secapi'])       # Security API
    coupon_api = CouponAPI(log=log, **config['coupon_api']) # Coupon API

    try:
        # Step-1: Console application start with 'AsOfDate' as an argument/parameter
        log.info(f"Application Started at {datetime.now()}")
        parser = argparse.ArgumentParser(description="Fetching security details for the provided BONDs")
        parser.add_argument("AsOfDate", type=str, help="Date for which the report should run")
        args = parser.parse_args()

        if args.AsOfDate is None:
            AsOfDate = datetime.now().strftime("%Y-%m-%d")
        else:
            date_obj = datetime.strptime(args.AsOfDate, "%Y-%m-%d")
            AsOfDate = date_obj.strftime("%Y-%m-%d")


        # Step-2: Fetch list of securities from TransactionDB for which rates need to be fetched
        log.info(f"Fetching securities for rate checks started at {datetime.now()}")
        securities = db.fetchSecuritiesToCheckRates(AsOfDate)
        log.info(f"Fetching BONDs for rate checks ends at {datetime.now()}")


        try:
            # Step-3.1: Call security API to fetch rate and set them to a dataframe
            security_batch_data : list = []     # List collection
            log.info(f"Starting security API calls at {datetime.now}")
            security_batch_data = secapi.fetch_security_details_batch(securities)    # List of tuples i.e., [{security, rate}]
            log.info(f"Completed security API call at {datetime.now()}")


            # Step-3.2: Call Coupon API to fetch Effective_Date for each securities and set them to a dataframe
            coupon_batch_data : list = []     # List of collection
            log.info(f"Starting coupon API calls at {datetime.now}")
            coupon_batch_data = coupon_api.fetch_coupon_details_batch(securities) # List of tuples i.e., [{security, Eff_Date}]
            log.info(f"Completed coupon API call at {datetime.now()}")


            # Step-4: Process the fetched (rate + Eff_Date) and set them to a dataframe
            if len(security_batch_data) == 0:
                log.info(f"No securities to check on: {AsOfDate}")
            else:
                log.info(f"Count of securities to check for {AsOfDate} : {len(security_batch_data)}")
                
                # convert security API result into dataframe
                security_df = pd.DataFrame(security_batch_data)     # {bondId, rate, asofDt}
                security_df["asOfDt"] = AsOfDate

                # convert coupon API result into another dataframe
                if coupon_batch_data and len(coupon_batch_data)>0:  # {bondId, rate, EffectiveDate, Source}
                    coupon_df = pd.DataFrame(coupon_batch_data)
                    coupon_df = coupon_df[["bondId", "EffectiveDate"]]
                else:
                    log.info(f"No Security with coupon data available for {AsOfDate}")
                    coupon_df = pd.DataFrame(colulmns=["bondId", "EffectiveDate"])  # This will set empty dataframe

                # merge both dataframe into one based on 'bondId'
                merged_df = pd.merge(
                    security_df[["bondId", "rate", "asOfDt"]],
                    coupon_df,
                    on="bondId",
                    how="left"  # Ensures all securities are taken from security_batch_data
                )

                # define column datatypes
                column_data_type = {
                    'asOfDt': object,
                    'bondId': str,
                    'rate': float,
                    'EffectiveDate': str
                }
                
                security_all_data = merged_df.astype(column_data_type)
                log.info(f"Security & Coupon APIs data conversion to dataframe completed at {datetime.now()}")


                # Stpe-5: Save the data into database table
                log.info(f"Starting db save at {datetime.now()}")
                result_count = db.save_data(security_all_data, AsOfDate)
                log.info(f"Completed db save at {datetime.now()}")

                # Step-6: Flag trades that have been re-rated
                log.info(f"Starting rerate flagging of trades at {datetime.now()}")
                result_count = db.setRerateData(AsOfDate)
                log.info(f"Completed rerate flagging of trades at {datetime.now()}")

        except Exception as e:
            log.error("An error occured %s", repr(e))
            raise SystemExit(-1)

    except Exception as e:
        log.error("An error occured %s", repr(e))
        raise SystemExit(-1)
    

if __name__ == "__main__":
    fetch_main()

