import logging
import logging.handlers


basic_formatter = logging.Formatter(
	fmt='[{levelname}] {message}',
	style='{')
detailed_formatter = logging.Formatter(
	fmt='[{asctime}] [{levelname}:{filename}:{lineno}] {message}',
	style='{')
basic_console_handler = logging.StreamHandler()
basic_console_handler.setLevel(logging.INFO)
basic_console_handler.setFormatter(basic_formatter)
detailed_console_handler = logging.StreamHandler()
detailed_console_handler.setLevel(logging.DEBUG)
detailed_console_handler.setFormatter(detailed_formatter)


def get_file_handler(filename: str) -> logging.Handler:
	handler = logging.handlers.RotatingFileHandler(
		filename=filename,
		maxBytes=1000000,
		backupCount=10,
		delay=True,
		encoding='utf8',
	)
	handler.setLevel(logging.DEBUG)
	handler.setFormatter(detailed_formatter)
	return handler


def init_logging(verbose: bool, log_filename: str):
	"""
	Initializes the Amanuensis logger settings
	"""
	logger = logging.getLogger("amanuensis")
	if log_filename:
		logger.addHandler(get_file_handler(log_filename))
		logger.setLevel(logging.DEBUG)
	elif verbose:
		logger.addHandler(detailed_console_handler)
		logger.setLevel(logging.DEBUG)
	else:
		logger.addHandler(basic_console_handler)
		logger.setLevel(logging.INFO)
