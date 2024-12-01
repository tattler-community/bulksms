"""Utility functions for bulksms library"""

import string
import os
from typing import Optional

def getenv(k: str, v: Optional[str]=None) -> Optional[str]:
    """Wrapper for os.getenv for mocking"""
    return os.getenv(k, v)                                  # pragma: no cover

def normalize_recipient(recipient: str) -> str:
    """Normalize a recipient's number or symbolic ID to the API's expected format.
    
    Mobile numbers: Extracts digits and replaces international calling code with +X form.

    e.g. '001 (232) 892-120 0123'    -> '+12328921200123'

    Symbolic recipients: strips any whitespace.

    :param
    """
    if set(recipient) & set(string.ascii_letters):
        # symbolic recipient, not numeric => strip only
        return recipient.strip()
    recipient = ''.join(d for d in recipient if d in string.digits)
    return '+' + recipient.lstrip('0')

