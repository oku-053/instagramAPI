from dotenv import load_dotenv
load_dotenv()

import os
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
APP_ID = os.getenv('APP_ID')
APP_SECRET = os.getenv('APP_SECRET')
INSTAGRAM_BUSINESS_ACCOUNT_ID = os.getenv('INSTAGRAM_BUSINESS_ACCOUNT_ID')
VERSION = os.getenv('v15.0')
GRAPH_DOMAIN = os.getenv('GRAPH_DOMAIN')
ENDPOINT_BASE = os.getenv('ENDPOINT_BASE')