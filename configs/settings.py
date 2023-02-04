import configparser
from distutils.util import strtobool
import os


conf_file_path = "configs/config_dev.ini"
if os.getenv("ENVIRONMENT") == "prod":
    conf_file_path = "configs/config_dev.ini"

conf = configparser.ConfigParser()
conf.read(conf_file_path)

log_file = conf["api"]["log_file"]
debug = strtobool(conf["api"]["debug"])
port = int(conf["api"]["port"])
