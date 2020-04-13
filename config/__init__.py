import os.path
import json

# Load the config data
with open(os.path.dirname(__file__) + '/../config.json') as json_file:
    CONFIG = json.load(json_file)
