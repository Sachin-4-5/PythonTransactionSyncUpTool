from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.engine import make_url, URL
from pyodbc import connect
from datetime import datetime
import pandas as pd
import warnings

warnings.filterwarnings('ignore')
timestamp = datetime.now()
timestamp_str1 = timestamp.strftime('%Y-%m-%d %H:%M:%S')


class DB:

    # below mentioned drivers must be installed inside server where this application will run to make successful db connection
    drivers = [
        'ODBC Driver 18 for SQL Server',
        'ODBC Driver 17 for SQL Server',
        'ODBC Driver 13 for SQL Server',
        'ODBC Driver 11 for SQL Server',
        'SQL Server Native Client 11.0',
        'SQL Server Native Client 10.0',
        'SQL Native Client',
        'SQL Client',
        'SQL Server'
    ]


    def __init__(self, connection_string, log):
        self.log=log
        for index, driver in enumerate(DB.drivers, start=1):       # enumerate() is a built-in function which adds an index counter.
            try:
                self.log.debug(f'Attempting to connect db using {driver}')
                connection_string = connection_string.replace("True", "YES")
                self.connection = connect(f"Driver={{{driver}}};{connection_string};")
                self.connection.autocommit = True
                self.log.info(f'connected to db using {driver}')
                self.connection.timeout = 6000
                return
            except Exception as e:
                if index < len(DB.drivers):
                    self.log.info(f'failed to connect using {driver}, trying another drivers\n{e}')
                else:
                    raise e 



    # Method for saving API data into database
    # Here, 'security_api_data_df' is basically a Pandas dataframe containing security API data 
    def save_data(self, security_api_data_df, AsOfDate):
        try:
            self.log.info('Inserting data')
            cursor = self.connection.cursor()
            data_to_insert = [      # It is a list comprehension that builds a list of tuple.
                (
                    row['rate'], 
                    row['EffectiveDate'],
                    row['bondId'], 
                    AsOfDate
                )
                for index, row in security_api_data_df.iterrows()
            ]

            query = """
                BEGIN
                    UPDATE [dbo].[tbl_RerateRecon]
                    SET [APIRate] = ? ,
                        [CpnEffectiveDate] = ?
                    WHERE [BOND] = ? AND [AsOfDate] = ? 
                END
            """

            cursor.fast_executemany = True
            cursor.executemany(query, data_to_insert)
            return len(security_api_data_df)

        except Exception as e:
            self.log.error(f"database write error: {str(e)}")
            raise SystemExit(-1)
    


    # Fetch all securities for the given AsOfDate that are eligible for the reports.
    def fetchSecuritiesToCheckRates(self, asofdate):
        print("Inside db method asofdate:" + asofdate)
        self.log.info('Fetching Bonds for rate check')
        try:
            cursor = self.connection.cursor()   # Creates a DB connection.
            query = "EXEC sp_GetBondForRates ?" # '?' is a placeholder for asofdate. Ex- EXEC sp_GetBondForRates '2025-08-30'
            self.log.info(query)
            cursor.execute(query, asofdate)     # Cursor used to run SQL commands.
            rows = cursor.fetchall()
            print(rows)

            securityIDList = [rows[0] for row in rows]  # List of all Securitiess/Bonds.
            return securityIDList
        
        except Exception as e:
            self.log.error(f"Fetching security for rate check error: {str(e)}")
            raise SystemExit(-1)



    # Method to flag trades that have been re-rated.
    def setRerateData(self, asofdate):
        self.log.info('Fetching Bonds for rate check')
        try:
            cursor = self.connection.cursor()
            query = "EXEC sp_set_RerateFlag"
            result = cursor.execute(query)
            return 0
        except Exception as e:
            self.log.error(f"Error while flagging rerated data: {str(e)}")
            raise e