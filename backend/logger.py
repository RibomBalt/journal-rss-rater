import logging
from .config import AppSettings, get_config

# class CustomAdapter(logging.LoggerAdapter):
#     def process(self, msg, kwargs):
#         custom_prefix = self.extra.get("custom_prefix", "")
#         return f"[{custom_prefix}] {msg}", kwargs

# TODO merge uvicorn logging as well
# https://stackoverflow.com/questions/77001129/how-to-configure-fastapi-logging-so-that-it-works-both-with-uvicorn-locally-and
def custom_logger(logger_name, debug=False):
    config = get_config()

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    # create file handler that logs debug and higher level messages
    fh = logging.FileHandler(config.LOG_OUTPUT)
    fh.setLevel(logging.DEBUG if config.DEBUG else logging.INFO)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG if config.DEBUG else logging.INFO)
    # create formatter and add it to the handlers
    formatter = logging.Formatter(
        '[%(asctime)s|%(name)s|%(levelname)s] %(message)s')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    # add the handlers to logger
    logger.addHandler(ch)
    logger.addHandler(fh)
    # logger_adapter = CustomAdapter(logger, {"custom_prefix": prefix})
    logger.propagate = False
    
    return logger