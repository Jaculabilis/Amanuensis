import logging

logger = logging.getLogger("amanuensis")
handler = logging.StreamHandler()
logger.addHandler(handler)

def log_normal():
	logger.setLevel(logging.INFO)
	handler.setLevel(logging.INFO)
	formatter = logging.Formatter('[{levelname}] {message}', style="{")
	handler.setFormatter(formatter)

def log_verbose():
	logger.setLevel(logging.DEBUG)
	handler.setLevel(logging.DEBUG)
	formatter = logging.Formatter('[{asctime}] [{levelname}:{filename}:{lineno}] {message}', style="{")
	handler.setFormatter(formatter)

log_normal()
