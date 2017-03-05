from hashlib import sha512
from django.conf import settings
KEYS = ('key', 'txnid', 'amount', 'productinfo', 'firstname', 'email',
        'udf1', 'udf2', 'udf3', 'udf4', 'udf5',  'udf6',  'udf7', 'udf8',
        'udf9',  'udf10')

def generate_hash(data):
    """
    Generates sha512 of form fields in following format.
    sha512(key|txnid|amount|productinfo|firstname|email|udf1|udf2|udf3|udf4|udf5||||||SALT)
    """
    hash_sum = sha512('')
    for key in KEYS:
        hash_sum.update("%s%s" % (str(data.get(key, '')), '|'))
    hash_sum.update(settings.PAYU_INFO.get('merchant_salt'))
    return hash_sum.hexdigest().lower()

def verify_hash(data):
    """
    Generates sha512 of received data fields in following format.
    sha512(SALT|status||||||udf5|udf4|udf3|udf2|udf1|email|firstname|productinfo|amount|txnid|key)
    """
    KEYS_REVERSED = KEYS[::-1]
    hash_sum = sha512('')
    hash_sum.update(settings.PAYU_INFO.get('merchant_salt'))
    hash_sum.update("%s%s" % ('|', str(data.get('status', ''))))
    for key in KEYS_REVERSED:
        hash_sum.update("%s%s" % ('|', str(data.get(key, ''))))
    return hash_sum.hexdigest().lower() == str(data.get('hash', ''))
