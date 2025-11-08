# Below config code is when we want to fetch all configuration values directly from config.ini
# But for fetching password related from some other application check cfg_main.py

import configparser
import os
from datetime import datetime

def read_cfg(cfg_file="config.ini", log=None):
    config = configparser.ConfigParser()
    if not os.path.exists(cfg_file):
        raise FileNotFoundError(f"Config file not found: {cfg_file}")

    config.read(cfg_file)

    # Store all configurations inside separate dictionary collections.
    # Database config
    db_config = {
        "connection_string": config.get("db", "connection_string")
    }

    # Security API config
    security_api_config = {
        "url": config.get("SECURITY_API", "URL", fallback=""),
        "token_key": config.get("SECURITY_API", "token_key", fallback=""),
        "user_key": config.get("SECURITY_API", "USER_key", fallback=""),
        "pwd_key": config.get("SECURITY_API", "PWD_key", fallback="")
    }

    # Coupon API config
    coupon_api_config = {
        "url": config.get("COUPON_API", "URL", fallback=""),
        "token_key": config.get("COUPON_API", "token_key", fallback=""),
        "user_key": config.get("COUPON_API", "USER_key", fallback=""),
        "pwd_key": config.get("COUPON_API", "PWD_key", fallback="")
    }

    # Log config
    raw_log_path = config.get("log", "path")
    log_path = raw_log_path.format(date=datetime.now().strftime("%Y-%m-%d"))
    log_config = {
        "path": log_path,
        "level": config.get("log", "level", fallback="INFO").upper()
    }

    cfg = {
        "db": db_config,
        "security_api": security_api_config,
        "coupon_api": coupon_api_config,
        "log": log_config
    }

    if log:
        log.info("Configuration loaded successfully")

    return cfg
