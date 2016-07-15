import base64
import datetime
import urllib
import urlparse
import hashlib
import hmac
import requests

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
        extra = extra or {}
        base_params = dict(
            Service='AWSECommerceService',
            AWSAccessKeyId=self.access_key,
            AssociateTag=self.associate_tag,
            Timestamp=formatted_amazon_datetime_str(),
            Operation=operation
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
        return response.content


class Lookup(AWS):

    version = '2013-08-01'

    def item_lookup(self, item_ids='', **kwargs):
        from parsers.lookup import ItemLookup
        """
        http://docs.aws.amazon.com/AWSECommerceService/latest/DG/ItemLookup.html

        :param item_ids:
        """
        extra = {'ItemId': item_ids}
        extra.update(kwargs)
        return ItemLookup.load(self.make_request('ItemLookup', extra=extra))
