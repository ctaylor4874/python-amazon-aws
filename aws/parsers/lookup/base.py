import functools
import re

from lxml import etree

from ..base import BaseElementWrapper, first_element_or_none


def parse_int(f):
    """
    Function wrapper to convert the returned value to an integer.
    :param f:
    :return:
    """
    def inner(*args, **kwargs):
        i = f(*args, **kwargs)
        if i:
            return int(i)
        return
    return inner


def parse_float(f):
    """
    Function wrapper to convert the returned value to a float.
    :param f:
    :return:
    """
    def inner(*args, **kwargs):
        i = f(*args, **kwargs)
        if i:
            x = re.sub('[^\d^\.]', '', i).strip('.')
            if not x:
                return
            return float(x)
        return
    return inner


def parse_bool(f):
    """
    Function wrapper to convert the returned value to a boolean.
    :param f:
    :return:
    """
    def inner(*args, **kwargs):
        i = f(*args, **kwargs)
        if i:
            return i == '1' or i.lower() == 'true'
        return
    return inner


def first_element(f):
    def inner(*args, **kwargs):
        i = f(*args, **kwargs)
        if i:
            return i[0].encode('ascii', errors='ignore')
        return
    return inner


class AWSError(Exception):

    def __init__(self, err_wrapper):
        self.err_wrapper = err_wrapper
        self.msg = err_wrapper.message
        self.code = err_wrapper.code
        Exception.__init__(self, '{} - {}'.format(self.code, self.msg))

    def __repr__(self):
        return '<{} code={} message={}>'.format(self.__class__.__name__, self.code, self.msg)


class ItemLookupRequestError(AWSError):
    pass


class BaseLookupWrapper(BaseElementWrapper):
    """
    Subclass of BaseElementWrapper to apply the namespace to an xpath function to reduce redundancy.
    """

    target_element_xpath = '//a:ItemLookupResponse'

    namespaces = {
        'a': 'http://webservices.amazon.com/AWSECommerceService/2011-08-01'
    }

    def __init__(self, element):
        BaseElementWrapper.__init__(self, element)
        # if element is None then we use a bogus xml element as to not throw an error when using partial.
        # this can lead to an exception (AttributeError: '_ElementStringResult' object has no attribute 'xpath')
        # when using an item plugin which wasn't requested. Ex creating a parser class using the Images plugin
        # without sending Images in the ResponseGroups param.
        self.xpath = functools.partial(self.element.xpath, namespaces=self.namespaces) if element is not None else lambda x: [etree._ElementStringResult()]


class BaseErrorWrapper(BaseLookupWrapper):
    """
    Used to parse and/or raise an error when a response has any Errors tag.
    """

    namespaces = {
        'a': 'http://ecs.amazonaws.com/doc/2005-10-05/'
    }

    def __init__(self, element):
        BaseLookupWrapper.__init__(self, element)

    @property
    @first_element
    def code(self):
        return self.xpath('./a:Code/text()')

    @property
    @first_element
    def message(self):
        return self.xpath('./a:Message/text()')

    def has_error(self):
        """
        If there's no message, then there's no error.
        :return:
        """
        return bool(self.message)

    def raise_for_error(self):
        """
        Raise an AWSError if an error exists.
        :return:
        """
        if self.has_error():
            raise AWSError(self)

    def as_error(self):
        if self.has_error():
            return AWSError(self)

    def __repr__(self):
        return '<{} code={} message={}>'.format(self.__class__.__name__, self.code, self.message)


class FullErrorResponseWrapper(BaseErrorWrapper):
    """
    Used to parse a response which is entirely an error.
    """

    @property
    @first_element
    def request_id(self):
        return self.xpath('./a:RequestId/text()')


class ItemLookupRequestErrorWrapper(BaseErrorWrapper):
    """
    Used to parse an ItemLookup response which has an error
    """

    namespaces = BaseLookupWrapper.namespaces

    def raise_for_error(self):
        """
        Raise an ItemLookupRequestError if an error exists.
        :return:
        """
        if self.has_error():
            raise ItemLookupRequestError(self)

    def as_error(self):
        if self.has_error():
            return ItemLookupRequestError(self)


class ItemLookupResponse(BaseLookupWrapper):

    target_element_xpath = '//a:ItemLookupResponse'

    def __init__(self, element, psr_cls):
        """

        :param element: The lxml.etree._Element class which is extracted from calling xpath.
        :param psr_cls: The parser class which is created by you to parse out the required data from the response.
            (~~~ Note that this must NOT be an instance of the parser class. Just simply a reference to the class. ~~~)
            see example_item_lookup.py
        """
        BaseLookupWrapper.__init__(self, element)
        # Check for any errors before continuing
        # else the OperationRequest.__init__ will throw an error.
        BaseErrorWrapper(element).raise_for_error()
        operation_request_element = self.xpath(OperationRequest.target_element_xpath)
        self.operation_request = OperationRequest(first_element_or_none(operation_request_element))
        self.items = Items(first_element_or_none(self.xpath(Items.target_element_xpath)), psr_cls)


class Items(BaseLookupWrapper):
    """
    Used to parse the Items child element in the response.
    """

    target_element_xpath = './a:Items'

    class Request(BaseLookupWrapper):

        target_element_xpath = './a:Request'

        @property
        @parse_bool
        @first_element
        def is_valid(self):
            return self.xpath('./a:IsValid/text()')

        @property
        @first_element
        def id_type(self):
            return self.xpath('./a:ItemLookupRequest/a:IdType/text()')

        @property
        def item_ids(self):
            return self.xpath('.//a:ItemLookupRequest/a:ItemId/text()')

        @property
        def response_groups(self):
            return self.xpath('.//a:ItemLookupRequest/a:ResponseGroup/text()')

        @property
        @first_element
        def variation_page(self):
            return self.xpath('./a:ItemLookupRequest/a:VariationPage/text()')

        @property
        def errors(self):
            return [ItemLookupRequestErrorWrapper(x) for x in self.xpath('.//a:Errors/a:Error')]

    def __init__(self, element, psr_cls):
        """

        :param element: The lxml.etree._Element class which is extracted from calling xpath.
        :param psr_cls: The parser class which is created by you to parse out the required data from the response.
            (~~~ Note that this must NOT be an instance of the parser class. ~~~)

        example psr_cls:
            >>> from aws.parsers.lookup import Offers, SalesRank
            >>>
            >>> class MyParserItem(Offers, SalesRank):
            >>>     pass
            >>>
            >>> i = Items(etree._Element(), MyParserItem)
        """
        BaseLookupWrapper.__init__(self, element)
        self.request = self.Request(first_element_or_none(self.xpath(self.Request.target_element_xpath)))
        self.psr_cls = psr_cls

    def item_list(self):
        return [self.psr_cls(x) for x in self.xpath('./a:Item')]


class OperationRequest(BaseLookupWrapper):

    target_element_xpath = './a:OperationRequest'

    @property
    def headers(self):
        return [(first_element_or_none(x.xpath('./@Name', namespaces=self.namespaces)),
                 first_element_or_none(x.xpath('./@Value', namespaces=self.namespaces)))
                for x in self.xpath('.//a:HTTPHeaders/a:Header')]

    @property
    @first_element
    def request_id(self):
        return self.xpath('./a:RequestId/text()')

    @property
    def arguments(self):
        return [(first_element_or_none(x.xpath('./@Name', namespaces=self.namespaces)),
                 first_element_or_none(x.xpath('./@Value', namespaces=self.namespaces)))
                for x in self.xpath('.//a:Arguments/a:Argument')]

    @property
    @parse_float
    @first_element
    def request_processing_time(self):
        return self.xpath('./a:RequestProcessingTime/text()')
