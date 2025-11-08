from socket import gethostname
from sys import stdout
from os import makedirs, getlogin
from os.path import dirname
from datetime import datetime
from logging import DEBUG, ERROR, Handler, FileHandler, StreamHandler, Handler, Filter, Formatter, basicConfig, getLogger


def init_log():
    
    # Initializes logging with console + memory handler (for replay).
    format_spec = '%(asctime)s - %(levelname)-8s - %(login)s@%(hostname)s - %(message)s'

    memory_handler = MemoryHandler()
    console_handler = StreamHandler(stdout)
    console_handler.setFormatter(Formatter(format_spec))
    memory_handler.setFormatter(Formatter(format_spec))

    basicConfig(level=DEBUG, format=format_spec, handlers=[memory_handler, console_handler])

    log = getLogger("PythonConsoleApp")
    log.format_events = memory_handler.format_events
    log.addFilter(UserHostFilter())
    log.contains_error = memory_handler.contains_error

    try:
        log.addHandler(FileHandler(filename="last-session.log", mode="w", encoding="utf-8"))
    except Exception as e:
        log.warning(f"Failed to attach log file in app dir. {e}")

    # Attach dynamic config function
    log.config = lambda path, form, level: _config_log(log, path, form, level, memory_handler)

    log.debug("Initialized logging")
    return log



def _config_log(log, path, form, level, memory_handler):
    
    #Configure log file location and replay memory logs to file.
    try:
        # Replace {date} placeholder with today's date
        path = path.format(date=datetime.today().strftime("%Y-%m-%d"))
        log.debug(f"Configuring logging to '{path}'")

        makedirs(dirname(path), exist_ok=True)
        file_handler = FileHandler(path, encoding="utf-8")
        file_handler.setFormatter(Formatter(form))
        log.addHandler(file_handler)
        log.setLevel(getattr(__import__("logging"), level.upper(), DEBUG))

        # Ensure all handlers share the same format
        for h in log.handlers:
            h.setFormatter(Formatter(form))

        # Replay past log records into file
        memory_handler.replay(file_handler)

    except Exception as e:
        log.error(f"Failed to configure log file {path}. {e}")



class MemoryHandler(Handler):
    # Stores log records in memory until a file is configured.
    def __init__(self) -> None:
        self.log_records = []
        super().__init__()

    def emit(self, record):
        self.log_records.append(record)

    def format_events(self):
        return '\n'.join([self.format(record) for record in self.log_records])

    def contains_error(self, search_string=None):
        def filter_func(record):
            return (
                record.levelno >= ERROR
                and (search_string is None or search_string in f"{record.filename}:{record.funcName}")
            )
        return any(filter(filter_func, self.log_records))

    def replay(self, other: Handler):
        for r in self.log_records:
            other.emit(r)



class UserHostFilter(Filter):
    # Adds hostname and login user info into every log record.
    hostname = gethostname()
    try:
        login = getlogin()
    except Exception:
        login = "unknown"

    def filter(self, record):
        record.hostname = UserHostFilter.hostname
        record.login = UserHostFilter.login
        return True