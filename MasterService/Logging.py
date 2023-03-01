import logging 
import time
import os
import sys


def app_log(msg):
    logging.info(msg, extra={
        'log_layer': 'App'
    })

def service_log(msg):
    logging.info(msg, extra={
        'log_layer': 'Service'
    })

def domain_log(msg):
    logging.info(msg, extra={
        'log_layer': 'Domain'
    })

def configure_logging(service_name):
    FORMAT = logging.Formatter('[' + service_name + '][%(log_layer)s][%(asctime)s]: %(message)s')
    logging.root.setLevel(logging.INFO)
    rootLogger = logging.getLogger()

    file_name = "{0}/{1}-{2}.log".format('logs/', service_name, time.ctime().replace(' ', '_').replace(':', '-'))
    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    fileHandler = logging.FileHandler(file_name)
    fileHandler.setFormatter(FORMAT)
    rootLogger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setFormatter(FORMAT)
    rootLogger.addHandler(consoleHandler)
    app_log('Initialized logging for ' + service_name)