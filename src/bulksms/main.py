"""Command-line interface to BulkSMS library"""

import argparse
import sys
from typing import Iterable, Tuple

from .utils import getenv
from .api import BulkSMS, DEFAULT_ROUTING_GROUP

def parse_args(args: Iterable[str]) -> argparse.Namespace:
    """Parse arguments provided and return configuration options.
    
    :param args:    List of arguments to parse.
    
    :return:        Config options expressed by arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("recipient", help="Recipient number or alphanumeric reference; may provide multiple separated by commas.")
    parser.add_argument("msg", help="Text message to deliver")
    parser.add_argument("-r", "--routing", required=False, help="Routing group to deliver message with", default=DEFAULT_ROUTING_GROUP)
    parser.add_argument("-s", "--sender", required=False, help="Sender ID to deliver message with")
    parser.add_argument("-t", "--token", required=False, help="Colon-separated token to use for authentication (name:secret); overrides BULKSMS_AUTH_TOKEN envvar")
    parser.add_argument("-l", "--login", required=False, help="Colon-separated login to use for authentication (username:password); overrides BULKSMS_AUTH_LOGIN envvar")
    return parser.parse_args(args)

def get_credentials() -> Tuple[str, str]:
    """Fetch credentials configured in the environment."""
    token = getenv('BULKSMS_AUTH_TOKEN')
    if token:
        if ':' not in token:
            raise ValueError("Invalid envvar BULKSMS_AUTH_TOKEN: does not contain ':' to separate token_id:token_secret")
        return dict(zip(['token_id', 'token_secret'], token.strip().split(':', 1)))
    login = getenv('BULKSMS_AUTH_LOGIN')
    if login:
        if ':' not in token:
            raise ValueError("Invalid envvar BULKSMS_AUTH_LOGIN: does not contain ':' to separate username:password")
        return dict(zip(['username', 'password'], login.strip().split(':', 1)))
    raise ValueError("Missing expected environment variables for credentials: BULKSMS_AUTH_TOKEN or BULKSMS_AUTH_LOGIN")


def main():
    """Entry point of command-line logic."""
    options = parse_args(sys.argv[1:])
    if options['token']:
        creds = dict(zip(['token_id', 'token_secret'], options['token'].split(':', 1)))
    elif options['login']:
        creds = dict(zip(['username', 'password'], options['token'].split(':', 1)))
    else:
        creds = get_credentials()
    bsms = BulkSMS(**creds)
    recipients = options['recipient'].split(',')
    bsms.send(recipients=recipients, content=options['msg'], priority=options['routing'], sender=options['sender'])

if __name__ == '__main__':
    main()