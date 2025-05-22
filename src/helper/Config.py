import configparser
import os


def get_config():
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    filePath = os.path.join(ROOT_DIR, '../../config.ini')
    config = configparser.ConfigParser()
    config.read(filePath)
    return config
