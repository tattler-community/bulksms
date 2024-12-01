"""Python client library to deliver SMS through BulkSMS.

Usage:

.. code-block:: python
    from bulksms import BulkSMS

    # get secrets from BulkSMS.com > login > Settings > Advanced > API Tokens
    bsms = BulkSMS(token_id='17A7C58921F54B5899D5C1237FCCD5FA-02-F', token_secret='9Sj8Ae9WQhBMEI2eMGXIKpZHC8shq')
    res = bsms.send(['+1535989656', '+4985656335'], "Happy birthday! Glückwunsch!", priority=True)
    print(res)

    # get delivery status
    bsms.msg_status(res)
"""

from .api import BulkSMS, DEFAULT_ROUTING_GROUP
