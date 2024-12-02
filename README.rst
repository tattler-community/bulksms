.. |badge_pipeline| image:: https://github.com/tattler-community/bulksms/actions/workflows/python-package.yml/badge.svg

.. |badge_coverage| image:: https://codecov.io/gh/tattler-community/bulksms/graph/badge.svg?token=neeCjCNfms
   :target: https://codecov.io/gh/tattler-community/bulksms

.. |badge_release| image:: https://img.shields.io/badge/Latest%20Release-1.0.0-blue

.. |badge_pyver| image:: https://img.shields.io/badge/py-3.9%20|%203.10%20|%203.11%20|%203.12-blue

.. |badge_license| image:: https://img.shields.io/badge/license-BSD_3--clause-blue


|badge_pipeline| |badge_coverage| |badge_release| |badge_pyver| |badge_license|


🚩 Table of contents
====================

1. `👀 What is bulksms?`_
2. `📌 Requirements`_
3. `🚀 Quick start`_
4. `💙 Help us be better`_
5. `🎖️ License`_

👀 What is bulksms?
===================

``bulksms`` is the simplest way to text people (send SMS) via python:

.. code-block:: python

   import bulksms

   bsms = bulksms.BulkSMS(token_id='17A7C58921F54B5899D5C1237FCCD5FA-02-F', token_secret='9Sj8Ae9WQhBMEI2eMGXIKpZHC8shq')

   bsms.send('+123456789', 'Hello world! 👋🏻')

``bulksms`` uses `BulkSMS.com <https://www.bulksms.com>`_ to deliver SMS.

Features
--------

This library allows you to:

- Send SMS to one recipient
- Bulk-send an SMS to many recipients at once
- Look up the delivery cost of a previous message
- Look up the delivery status of a previous message
- Customize the delivery type to trade time with cost
- Customize the sender ID e.g. to your mobile number or a company name
- Send "long SMS" exceeding the single-message length, using SMS concatenation
- Send messages with plain text (160 characters/message) or Unicode, e.g. emojis (67 characters/message)

📌 Requirements
==================

- Python version between 3.9 and 3.12
- An account at `BulkSMS.com <https://www.bulksms.com>`_ with some delivery credits
- If you want to use custom sender IDs (e.g. your company name or your own mobile number), you need to have them configured in your BulkSMS account.
- You need internet connectivity and HTTPS open towards ``api.bulksms.com`` to reach the delivery API


🚀 Quick start
=================

Install the ``bulksms`` library into it:

.. code-block:: bash

   pip install bulksms

Write some code to deliver messages:

.. code-block:: python

   import bulksms

   # authenticate to BulkSMS with token data (log into BulkSMS > Settings > Advanced > API Tokens)
   bsms = bulksms.BulkSMS(token_id='17A7C58921F54B5899D5C1237FCCD5FA-02-F', token_secret='9Sj8Ae9WQhBMEI2eMGXIKpZHC8shq')
   bsms.send('+123456789', 'Hello world! 👋🏻')

Done!

Here's some more advanced use-cases to deliver SMS:

.. code-block:: python

   import bulksms

   bsms = bulksms.BulkSMS(token_id='17A7C58921F54B5899D5C1237FCCD5FA-02-F', token_secret='9Sj8Ae9WQhBMEI2eMGXIKpZHC8shq')

   # send a message with a custom mobile number as Sender
   bsms.send('+123456789', 'Hello world! 👋🏻', sender='+1666777888')
   # send a message with a custom brand as SenderID
   bsms.send('+123456789', 'Hello world! 👋🏻', sender='Google inc')

   # send a text to a bunch of receivers in bulk
   bsms.send(['+123456789', '+4985296345', '+44785612458'], 'Hello world! 👋🏻')

   # send a text message with top priority
   bsms.send('+123456789', 'Hello world! 👋🏻', priority=True)

And here's some inspection use-cases:

.. code-block:: python

   import bulksms

   bsms = bulksms.BulkSMS(token_id='17A7C58921F54B5899D5C1237FCCD5FA-02-F', token_secret='9Sj8Ae9WQhBMEI2eMGXIKpZHC8shq')

   # look up what's the current delivery status of a message
   msgid = bsms.send('+123456789', 'Hello world! 👋🏻')

   dstatus = bsms.msg_delivery_status(msgid)
   # dstatus is in {'ACCEPTED', 'SCHEDULED', 'SENT', 'DELIVERED', 'FAILED'}

   dcost = bsms.msg_cost(msgid)
   # dcost is a float showing the number of credits consumed to deliver the message


💙 Help us be better
=======================

Here's how you can help:

- ⭐️ star our `repository <https://github.com/tattler-community/bulksms/>`_ if you like bulksms.
- Mention bulksms in any of your online posts so people find out about it.

And if you're a developer:

- Report any `issue <https://github.com/tattler-community/bulksms/issues>`_ in our code or docs. We take those seriously.
- Package bulksms for your distribution. Else Ubuntu, Debian, CentOS and FreeBSD will serve the most people.


🎖️ License
=============

``bulksms`` is open-source software (BSD 3-clause license).
