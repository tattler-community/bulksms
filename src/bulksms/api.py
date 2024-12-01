"""Python library to deliver SMS messages through BulkSMS.com.

It relies on BulkSMS's JSON API, see https://www.bulksms.com/developer/json/v1/ for details.

Usage:

bsms = BulkSMS(token_id='17A7C58921F54B5899D5C1237FCCD5FA-02-F', token_secret='9Sj8Ae9WQhBMEI2eMGXIKpZHC8shq', sender='MyCoolService.com')
res = bsms.send(['+1535989656', '+4985656335'], "Happy birthday! Glückwunsch!", priority=True)
print(res)
"""

import logging
import json
import base64
from typing import Optional, Mapping, Iterable, Union, Any

import urllib.request
import urllib.parse

from bulksms.utils import getenv, normalize_recipient

# See https://www.bulksms.com/pricing/sms-routing.htm
ROUTING_GROUPS = [ 'ECONOMY', 'STANDARD', 'PREMIUM' ]
DEFAULT_ROUTING_GROUP = ROUTING_GROUPS[0]

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


class BulkSMS:
    """Holds an authenticated session with BulkSMS.com's JSON API.
    
    See https://www.bulksms.com/developer/json/v1/ for API details.    
    """

    api_base = 'https://api.bulksms.com/v1'
    timeout_s = 4

    def __init__(self, token_id: Optional[str]=None, token_secret: Optional[str]=None, username: Optional[str]=None, password: Optional[str]=None, sender: Optional[str]=None, routing_group: Optional[str]=None):
        """Initialize the object.
        
        :param token_id:		Token name, if token access is used.
        :param token_secert:	Token secret, if token access is used.
        :param username:		Username, if login is used.
        :param password:		Password, if login is used.
        :param sender:			Sender ID to use as From when sending messages, number or alphanumeric; must be pre-configured in BulkSMS account.
        :param routing_group:	Name of the routing group (priority) to use, in { 'ECONOMY', 'STANDARD', 'PREMIUM' }. See https://www.bulksms.com/pricing/sms-routing.htm .

        :raises ValueError:		Authentication data is lacking, or invalid routing_group.
        """
        if token_id is None and username is None:
            raise ValueError("Either token or username/password must be given.")
        self.login = {
            'username': username or token_id,
            'password': password or token_secret,
        }
        self.sender = None
        if sender is not None:
            self.sender = normalize_recipient(sender)
        if routing_group:
            self.routing_group = routing_group
        else:
            self.routing_group = getenv('BULKSMS_DEFAULT_ROUTING', DEFAULT_ROUTING_GROUP)
        self.routing_group = self.routing_group.upper()
        if self.routing_group not in ROUTING_GROUPS:
            raise ValueError(f"Invalid routing_group '{routing_group}': valid choices are {ROUTING_GROUPS}")
        assert self.routing_group in ROUTING_GROUPS

    def get_headers(self) -> Mapping[str, str]:
        """Generate generic request headers, e.g. with authentication data.
        
        :return:	Map with HTTP header names to values."""
        astr = f"{self.login['username']}:{self.login['password']}"
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Basic {base64.b64encode(astr.encode()).decode()}'
            }

    def do_send(self, url: str, content: bytes=b'', method: str='GET', js: Optional[Any]=None) -> Any:
        """Low-level interface to send a raw message to the BulkSMS API endpoint.
        
        The request-specific return value is a list of objects, each looking like this for 'message' delivery.

        :param url:			URL to send the request to.
        :param content:		Raw content to send.
        :param method:		HTTP method to query endpoint with.
        :param js:			Any JSON object to send; if given along with 'content', then it's appended to it.

        :return:			The JSON data returned by BulkSMS' JSON endpoint.
        """
        log.debug("Sending req to: %s", url)
        headers= self.get_headers()
        log.debug(headers)
        if js is not None:
            content += json.dumps(js).encode()
        method = method.upper()
        log.debug("Sending %s to %s with %s", method, url, content)
        req = urllib.request.Request(url, method=method.upper(), data=content, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_s) as f:
                return json.loads(f.read().decode())
        except Exception as e:
            log.error("Error submitting request to %s: %s", url, e)
            raise

    def get_url(self, resource: str, params: Optional[Mapping[str, str]]=None) -> str:
        """Construct the final URL for a given resource and with given parameters.
        
        :param resource:	Name of BulkSMS resource within BulkSMS API, e.g. 'messages'.
        :param params:		Parameter names and values to append to the query string.

        :return:			Final URL with API base, resource, and parameters encoded.
        """
        url = self.api_base + '/' + resource.lstrip('/')
        if params is None:
            return url
        return url + '?' + urllib.parse.urlencode(params)

    def get_sender(self, sender: str=None) -> str:
        """Configure the sender ID, or return the currently configured sender ID.
        
        :param sender:	Value to configure, or None to leave unchanged.
        
        :return:		The sender that will be used."""
        if sender is None:
            return self.sender
        return normalize_recipient(sender)

    def get_routing_group(self, priority: bool=False) -> str:
        """Return the routing group to use based on local configuration and requested priority.
        
        :param priority:    Set to True to get name of highest-priority routing group; False to use session-default.

        :return:    Name of routing group to use.
        """
        if priority:
            return ROUTING_GROUPS[-1]
        return self.routing_group

    def send(self, recipients: Union[str,Iterable[str]], content: str, sender: Optional[str]=None, priority: bool=False) -> Iterable[str]:
        """Send message to some recipients.

        Plain text messages fit up to 160 characters per message. Messages with one or more UTF-8 characters fit
        up to 70 characters per message. The method automatically detects the optimal encoding.

        :param recipients:	Recipient or list of recipients to send to, either as mobile number or alphanumeric name.
        :param content:		Text of the message to send; may contain UTF-8 characters.
        :param sender:		Sender ID to override the session-default Sender ID, used if this is left unset.
        :param priority:	Whether the message should be sent requesting the top priority routing, or with the session-default routing priority.

        :raises urllib.error.URLError:   Failure communicating with BulkSMS' API.

        :return:			List with one message ID for each respective recipient.
        """
        if isinstance(recipients, str):
            recipients = [recipients]
        recipients = [normalize_recipient(r) for r in recipients]
        try:
            content.encode('ascii')
            enc_type = 'TEXT'
        except UnicodeEncodeError:
            enc_type = 'UNICODE'
        params = {
            'to': recipients,
            'encoding': enc_type,
            'body': content,
            'routingGroup': self.get_routing_group(priority)
        }
        if sender or self.sender:
            params['from'] = normalize_recipient(sender) if sender else self.sender
        try:
            res = self.do_send(self.get_url('messages'), js=params, method='POST')
        except Exception as e:
            log.error("Message to %s failed to send: %s", recipients, e)
            raise
        log.debug("Message to %s successfully sent: %s", recipients, res)
        return [msg['id'] for msg in res]
    
    def msg_status(self, message_id: str) -> Iterable[Mapping[str, Any]]:
        """Return raw message delivery status.
        
        :param message_id:   ID to get delivery status for.
        
        :return:        Status as described by BulkSMS API"""
        filter_params = {
            'type': 'SENT',
        }
        params = {
            'filter': urllib.parse.urlencode(filter_params)
        }
        return self.do_send(self.get_url(f'messages/{message_id}', params))

    def msg_delivery_status(self, message_id: str):
        """Return delivery status in {'ACCEPTED', 'SCHEDULED', 'SENT', 'DELIVERED', 'FAILED'}.
        
        :param message_id:   The message ID to look up delivery status for.
        
        :raises ValueError:             Server response breached expected format.
        :raises urllib.error.URLError:   Failure communicating with BulkSMS' API.

        :return:      Delivery status in {'ACCEPTED', 'SCHEDULED', 'SENT', 'DELIVERED', 'FAILED'}"""
        res = self.msg_status(message_id)
        try:
            return res['status']['type'].upper()
        except (KeyError, IndexError, TypeError, ValueError) as err:
            raise ValueError(f"Unable to parse result from server: '{res}'") from err

    def msg_cost(self, message_id: str) -> int:
        """Return cost of message delivery in credits.
        
        :param message_id:   The message ID to look up delivery status for.
        
        :return:      The cost of the message in number of credits.
        """
        res = self.msg_status(message_id)
        try:
            return float(res['creditCost'])
        except (KeyError, IndexError, TypeError, ValueError) as err:
            raise ValueError(f"Unable to parse result from server: '{res}'") from err
