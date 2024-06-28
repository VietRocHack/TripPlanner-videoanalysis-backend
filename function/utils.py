import logging

def setup_logger(name, log_file, level=logging.DEBUG):
	formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
	handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")        
	handler.setFormatter(formatter)

	logger = logging.getLogger(name)
	logger.setLevel(level)
	logger.addHandler(handler)

	return logger
