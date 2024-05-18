from logging import getLogger, DEBUG
import os

debug_logger = getLogger('debug_logger')
debug_logger.setLevel(DEBUG)

get_slack_access_token_api_uri = os.environ['GET_ACCESS_TOKEN_API_URI']
api_password = os.environ['API_PASSWORD']
slack_reactions_add_api_uri = os.environ['SLACK_REACTIONS_ADD_API_URI']