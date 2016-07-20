import logging
from functools import wraps

from lxml import etree


def first_element_or_none(element_list):
    """
    Return the first element or None from an lxml selector result.
    :param element_list: lxml selector result
    :return:
    """
    if len(element_list):
        return element_list[0]
    return


def first_element(f):
    """
    function wrapper for _first_element_or_none.

    This is equivalent to using `return _first_element_or_none(xpath())`.
    :param f:
    :return:
    """
    @wraps
    def inner(*args, **kwargs):
        return first_element_or_none(f(*args, **kwargs))
    return inner


class BaseElementWrapper(object):

    def __init__(self, element):
        """

        :param element: Etree object of response body
        """
        self.element = element
        self.logger = logging.getLogger(self.__class__.__name__)

    def __str__(self):
        if self.element is not None:
            return etree.tostring(self.element)
        return '<Element Non Existent>'

    @classmethod
    def load(cls, xml_string):
        """
        Create an instance of this class using an xml string.

        :param xml_string:
        :return:
        """
        tree = etree.fromstring(xml_string)
        return cls(tree)
