"""Testing logic for BulkSMS API"""

import json
import unittest
import os
import urllib.error
import urllib.request
import base64
from unittest import mock

from bulksms.api import BulkSMS, ROUTING_GROUPS, DEFAULT_ROUTING_GROUP

class BulkSMSTest(unittest.TestCase):

    """Test cases for BulkSMS object"""

    def test_constructor_fails_missing_auth(self):
        """Constructor raises if authentication data is not provided"""
        with self.assertRaises(ValueError) as err:
            BulkSMS()
        self.assertIn('token', str(err.exception))
        self.assertIn('username', str(err.exception))

    def test_constructor_fails_invalid_routing_envvar(self):
        """Constructor takes raises if routing group is invalid"""
        # with mock.patch('bulksms.api.DEFAULT_ROUTING_GROUP', new='foogroup'):
        with self.assertRaises(ValueError) as err:
            BulkSMS('tokid', 'tokpass', routing_group='foogroup')
        self.assertIn('routing_group', str(err.exception))

    def test_constructor_takes_routing_group_envvar(self):
        """Constructor takes routing group from envvar before default"""
        with mock.patch('bulksms.api.getenv') as menv:
            for rgroup in ROUTING_GROUPS:
                menv.side_effect = lambda k,v=None: {'BULKSMS_DEFAULT_ROUTING': rgroup }.get(k, os.getenv(k, v))
                bsms = BulkSMS('ti', 'ts')
                self.assertEqual(rgroup, bsms.get_routing_group())
                self.assertEqual(1, menv.call_count)
                menv.reset_mock()

    def test_constructor_honors_default_routing_group_envvar(self):
        """Constructor takes routing group from envvar before default"""
        with mock.patch('bulksms.api.getenv') as menv:
            for rgroup in ROUTING_GROUPS:
                menv.side_effect = lambda k,v=None: {'BULKSMS_DEFAULT_ROUTING': v }.get(k, os.getenv(k, v))
                with mock.patch('bulksms.api.DEFAULT_ROUTING_GROUP', new=rgroup):
                    bsms = BulkSMS('ti', 'ts')
                    self.assertEqual(rgroup, bsms.get_routing_group())

    def test_constructor_honors_sender(self):
        """Constructor honors sender argument"""
        bsms = BulkSMS('ti', 'ts')
        self.assertIsNone(bsms.get_sender())
        bsms = BulkSMS('ti', 'ts', sender='sender321')
        self.assertEqual('sender321', bsms.get_sender())

    def test_get_sender_normalizes(self):
        """get_sender() normalizes sender"""
        bsms = BulkSMS('ti', 'ts')
        self.assertEqual('asd', bsms.get_sender('asd'))
        self.assertEqual('Asd', bsms.get_sender(' Asd  '))

    def test_send_interface(self):
        """send() calls API Endpoint with expected auth headers and body data"""
        with mock.patch('bulksms.api.urllib.request.urlopen') as muop:
            muop.return_value.__enter__.return_value.read.return_value = b'[{"id": "68953asd"}]'
            bsms = BulkSMS('ti', 'ts')
            msg_body = "Read some books"
            bsms.send(['1234'], msg_body)
            self.assertEqual(1, muop.call_count)
            self.assertIsInstance(muop.call_args.args[0], urllib.request.Request)
            self.assertIn('Authorization', muop.call_args.args[0].headers)
            want_auth = base64.b64encode(b'ti:ts').decode()
            self.assertEqual(f'Basic {want_auth}', muop.call_args.args[0].headers['Authorization'])
            jdata = json.loads(muop.call_args.args[0].data.decode())
            self.assertIsInstance(jdata, dict)
            self.assertIn("encoding", jdata)
            self.assertIn("body", jdata)
            self.assertNotIn("from", jdata)
            self.assertIn("to", jdata)
            self.assertIsInstance(jdata["to"], list)
            self.assertEqual(["+1234"], jdata['to'])
            self.assertIn("routingGroup", jdata)
            self.assertEqual(DEFAULT_ROUTING_GROUP, jdata["routingGroup"])

    def test_send_accepts_single_recipient_str(self):
        """send() accepts a single recipient"""
        with mock.patch('bulksms.api.urllib.request.urlopen') as muop:
            muop.return_value.__enter__.return_value.read.return_value = b'[{"id": "68953asd"}]'
            bsms = BulkSMS('ti', 'ts')
            bsms.send('1234', 'My msg')
            self.assertEqual(1, muop.call_count)
            self.assertIsInstance(muop.call_args.args[0], urllib.request.Request)
            self.assertIn('Authorization', muop.call_args.args[0].headers)
            want_auth = base64.b64encode(b'ti:ts').decode()
            self.assertEqual(f'Basic {want_auth}', muop.call_args.args[0].headers['Authorization'])
            self.assertIn(b'"to": ["+1234"]', muop.call_args.args[0].data)
            self.assertNotIn(b'"from":', muop.call_args.args[0].data)

    def test_send_autodetects_encoding(self):
        """send() automatically sets 'encoding' field for content type"""
        with mock.patch('bulksms.api.urllib.request.urlopen') as muop:
            muop.return_value.__enter__.return_value.read.return_value = b'[{"id": "68953asd"}]'
            bsms = BulkSMS('ti', 'ts')
            for content, want_encoding in {
                '': 'TEXT',
                'My msg': 'TEXT',
                '🙂': 'UNICODE',
                'Lies bücher': 'UNICODE' }.items():
                bsms.send('1234', content)
                self.assertEqual(1, muop.call_count)
                self.assertIsInstance(muop.call_args.args[0], urllib.request.Request)
                jdata = json.loads(muop.call_args.args[0].data.decode())
                self.assertIsInstance(jdata, dict)
                self.assertIn("encoding", jdata)
                self.assertEqual(jdata["encoding"], want_encoding)
                self.assertIn("body", jdata)
                self.assertEqual(jdata["body"], content)
                muop.reset_mock()

    def test_send_allows_customizing_sender(self):
        """send() parameter sender overrides session-default"""
        with mock.patch('bulksms.api.urllib.request.urlopen') as muop:
            muop.return_value.__enter__.return_value.read.return_value = b'[{"id": "68953asd"}]'
            bsms = BulkSMS('ti', 'ts')
            msg_body = "Read some books"
            for snd in ['+49123456789', '213asd', 'foobar']:
                bsms.send(['1234'], msg_body, sender=snd)
                self.assertEqual(1, muop.call_count)
                self.assertIsInstance(muop.call_args.args[0], urllib.request.Request)
                jdata = json.loads(muop.call_args.args[0].data.decode())
                self.assertIn("from", jdata)
                self.assertEqual(snd, jdata["from"])
                muop.reset_mock()

    def test_send_honors_priority(self):
        """send() parameter sender overrides session-default"""
        with mock.patch('bulksms.api.urllib.request.urlopen') as muop:
            muop.return_value.__enter__.return_value.read.return_value = b'[{"id": "68953asd"}]'
            bsms = BulkSMS('ti', 'ts')
            bsms.send(['1234'], "Some body", priority=True)
            self.assertEqual(1, muop.call_count)
            self.assertIsInstance(muop.call_args.args[0], urllib.request.Request)
            jdata = json.loads(muop.call_args.args[0].data.decode())
            self.assertIn("routingGroup", jdata)
            self.assertEqual("PREMIUM", jdata["routingGroup"])

    def test_send_propagates_api_exceptions(self):
        """send() raises errors occurred while communicating with BulkSMS API"""
        with mock.patch('bulksms.api.urllib.request.urlopen') as muop:
            muop.side_effect = urllib.error.URLError("Bad network error")
            bsms = BulkSMS('ti', 'ts')
            with self.assertRaises(urllib.error.URLError) as err:
                bsms.send(['1234'], 'My msg')
            self.assertIn('Bad network error', str(err.exception))

    def test_msg_delivery_status(self):
        """msg_delivery_status() calls expected API Endpoint"""
        with mock.patch('bulksms.api.urllib.request.urlopen') as muop:
            bsms = BulkSMS('ti', 'ts')
            for result in ['ACCEPTED', 'SCHEDULED', 'SENT', 'DELIVERED', 'FAILED']:
                answer = b'{"status": {"type": "%s"}}' % result.encode()
                muop.return_value.__enter__.return_value.read.return_value = answer
                subid = '5544332211'
                self.assertEqual(result, bsms.msg_delivery_status(subid))
                self.assertEqual(1, muop.call_count)
                self.assertIsInstance(muop.call_args.args[0], urllib.request.Request)
                self.assertIn('Authorization', muop.call_args.args[0].headers)
                want_auth = base64.b64encode(b'ti:ts').decode()
                self.assertEqual(f'Basic {want_auth}', muop.call_args.args[0].headers['Authorization'])
                self.assertIn(f'/messages/{subid}', muop.call_args.args[0].full_url)
                muop.reset_mock()

    def test_msg_delivery_status_raises_api_error(self):
        """msg_delivery_status() raises when failing to communicate with API"""
        with mock.patch('bulksms.api.urllib.request.urlopen') as muop:
            muop.side_effect = urllib.error.URLError("Horrible L7 failure")
            bsms = BulkSMS('ti', 'ts')
            with self.assertRaises(urllib.error.URLError) as err:
                bsms.msg_delivery_status('12345')
            self.assertIn("Horrible L7 failure", str(err.exception))

    def test_msg_delivery_status_raises_bad_response(self):
        """msg_delivery_status() raises when API response is malformatted"""
        with mock.patch('bulksms.api.urllib.request.urlopen') as muop:
            bsms = BulkSMS('ti', 'ts')
            for resp in [
                '[]',
                '{"status": {}}',
                '{"status": {"t": "ACCEPTED"}}',
                '{"status": {"type2": "ACCEPTED"}}',
            ]:
                muop.return_value.__enter__.return_value.read.return_value = resp.encode()
                with self.assertRaises(ValueError) as err:
                    bsms.msg_delivery_status('12345')
                self.assertIn("Unable to parse", str(err.exception))

    def test_msg_cost(self):
        """msg_cost() returns API price value"""
        with mock.patch('bulksms.api.urllib.request.urlopen') as muop:
            bsms = BulkSMS('ti', 'ts')
            for cost in [1, 0.5, 1.22, 1234]:
                answer = '{"status": {"type": "DELIVERED"},"creditCost": %s}' % cost
                muop.return_value.__enter__.return_value.read.return_value = answer.encode()
                subid = '5544332211'
                self.assertEqual(cost, bsms.msg_cost(subid))
                self.assertEqual(1, muop.call_count)
                self.assertIsInstance(muop.call_args.args[0], urllib.request.Request)
                self.assertIn('Authorization', muop.call_args.args[0].headers)
                want_auth = base64.b64encode(b'ti:ts').decode()
                self.assertEqual(f'Basic {want_auth}', muop.call_args.args[0].headers['Authorization'])
                self.assertIn(f'/messages/{subid}', muop.call_args.args[0].full_url)
                muop.reset_mock()

    def test_msg_cost_raises_api_error(self):
        """msg_delivery_status() raises when failing to communicate with API"""
        with mock.patch('bulksms.api.urllib.request.urlopen') as muop:
            muop.side_effect = urllib.error.URLError("Horrible L7 failure")
            bsms = BulkSMS('ti', 'ts')
            with self.assertRaises(urllib.error.URLError) as err:
                bsms.msg_cost('12345')
            self.assertIn("Horrible L7 failure", str(err.exception))

    def test_msg_cost_raises_bad_response(self):
        """msg_delivery_status() raises when API response is malformatted"""
        with mock.patch('bulksms.api.urllib.request.urlopen') as muop:
            bsms = BulkSMS('ti', 'ts')
            for resp in [
                '[]',
                '{"status": {"type": "DELIVERED"},"creditCost":"asd"}',
                '{"status": {"type": "DELIVERED"},"creditCost":null}',
            ]:
                muop.return_value.__enter__.return_value.read.return_value = resp.encode()
                with self.assertRaises(ValueError, msg=f"msg_cost() raises ValueError upon unparsable response '{resp}'") as err:
                    bsms.msg_cost('12345')
                self.assertIn("Unable to parse", str(err.exception))


if __name__ == '__main__':
    unittest.main()         # pragma: no cover
