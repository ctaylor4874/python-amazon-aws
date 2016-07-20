import base64
import datetime
import urllib
import urlparse
import hashlib
import hmac
import os

import requests

import config

MARKETPLACES = {
    'us': 'webservices.amazon.com',
    'br': 'webservices.amazon.com.br',
    'ca': 'webservices.amazon.ca',
    'cn': 'webservices.amazon.cn',
    'de': 'webservices.amazon.de',
    'es': 'webservices.amazon.es',
    'fr': 'webservices.amazon.fr',
    'in': 'webservices.amazon.in',
    'it': 'webservices.amazon.it',
    'jp': 'webservices.amazon.jp',
    'mx': 'webservices.amazon.com.mx',
    'uk': 'webservices.amazon.co.uk'
}


def convert_to_gmtime(dt):
    """
    Convert the supplied date to GMT.
    :param dt:
    :return: parameter converted to GMT.
    """
    # Get the local time offset from gmt. Added 1 second to account for the time the computer takes to
    # generate utcnow and now.
    hr_diff = (((datetime.datetime.utcnow() - datetime.datetime.now()).seconds + 1) / 60) / 60
    return dt + datetime.timedelta(hours=hr_diff)


def formatted_amazon_datetime_str(dt=None):
    """
    Format a datetime object to amazon timestamp format spec. (YYYY-MM-DDThh:mm:ssZ) where T and Z are literals.
    :param dt: optional datetime to suppy. If none supplied, then use current datetime.
    :return: Formatted timestamp to use in request url.
    """
    dt = dt or datetime.datetime.now()
    gmtime = convert_to_gmtime(dt)
    return gmtime.strftime('%Y-%m-%dT%H:%M:%S.000Z')


def write_response(content, name):
    if config.WRITE_RESPONSES:
        with open(os.path.join(config.XML_RESPONSE_DIR, name), 'wb') as f:
            f.write(content)


class AWS(object):

    version = ''

    def __init__(self, associate_tag, access_key, secret_key, marketplace=None):
        """

        :param associate_tag: An alphanumeric token that uniquely identifies you as an Associate.
        :param access_key: Your AWS Access Key ID which uniquely identifies you.
        :param secret_key: A key that is used in conjunction with the Access Key ID
            to cryptographically sign an API request.
        :param marketplace: The locale where you are making the request.
        """
        self.associate_tag = associate_tag
        self.access_key = access_key
        self.secret_key = secret_key
        self.marketplace = marketplace or MARKETPLACES['us']

    def generate_signature(self, url_params):
        canonical_string = '&'.join(sorted(url_params.split('&')))
        string_to_sign = "GET\n{endpoint}\n/onca/xml\n{params}".format(endpoint=self.marketplace,
                                                                       params=canonical_string)
        signature = base64.b64encode(hmac.new(self.secret_key, string_to_sign, hashlib.sha256).digest())
        encoded_signature = urllib.quote(signature)
        return encoded_signature

    def make_request(self, operation, extra=None):
        """

        :param operation: Specifies the Product Advertising API operation to execute. For more information, see Operations.
            http://docs.aws.amazon.com/AWSECommerceService/latest/DG/CHAP_OperationListAlphabetical.html
        :param extra: Any extra parameters which are required for a specific operation.
        :return: AWS API Response content. Default XML String.
        """
        extra = extra or {}
        base_params = dict(
            AssociateTag=self.associate_tag,
            AWSAccessKeyId=self.access_key,
            Operation=operation,
            Service='AWSECommerceService',
            Timestamp=formatted_amazon_datetime_str()
        )
        base_params.update(extra)
        url_params = '&'.join(sorted(urllib.urlencode(base_params).split('&')))
        signature = self.generate_signature(url_params)
        url_params += '&Signature=%s' % signature
        url = urlparse.urlunsplit((
            'http',
            self.marketplace,
            '/onca/xml',
            url_params,
            None
        ))
        response = requests.get(url)
        content = response.content
        write_response(content, '{}Response.xml'.format(operation))
        return content


class Lookup(AWS):

    version = '2013-08-01'

    def item_lookup(self, item_ids=(), response_groups=(), **kwargs):
        """
        http://docs.aws.amazon.com/AWSECommerceService/latest/DG/ItemLookup.html

        :param item_ids:
        """
        extra = {'ItemId': ','.join(item_ids), 'ResponseGroup': ','.join(response_groups)}
        extra.update(kwargs)
        r = self.make_request('ItemLookup', extra=extra)
        return r
