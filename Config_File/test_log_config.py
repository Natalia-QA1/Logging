import logging.config
import yaml

# Load logging configuration from YAML file
with open('Config/config.yaml', 'r') as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)


#TESTING
logging.error('something went wrong')  # should not be sent
logging.error('error')  # email subject should be Errors Logs
logging.critical('production is down')  # email subject should be changed >Attention! Critical error!
logging.critical('something failed')  # email subject should be changed >Attention! Critical error!/despite 'something'
