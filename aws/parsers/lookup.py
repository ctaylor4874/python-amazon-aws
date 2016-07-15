import functools
import re

from base import BaseElementWrapper, first_element


namespaces = {
    'a': 'http://webservices.amazon.com/AWSECommerceService/2011-08-01'
}


def convert_to_int(f):
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


def convert_to_float(f):
    """
    Function wrapper to convert the returned value to a float.
    :param f:
    :return:
    """
    def inner(*args, **kwargs):
        i = f(*args, **kwargs)
        if i:
            return float(re.sub('[^\d^\.]', '', i))
        return
    return inner


def convert_to_bool(f):
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


class BaseLookupWrapper(BaseElementWrapper):
    """
    Subclass of BaseElementWrapper to apply the namespace to an xpath function to reduce redundancy.
    """

    def __init__(self, element):
        BaseElementWrapper.__init__(self, element)
        self.xpath = functools.partial(self.element.xpath, namespaces=namespaces)


class Offer(BaseLookupWrapper):
    """
    Used to parse out the ItemLookupResponse.Items.Item.Offers.Offer.
    """

    @property
    @first_element
    def merchant_name(self):
        return self.xpath('//a:Merchant/a:Name/text()')

    @property
    @first_element
    def offer_condition(self):
        return self.xpath('//a:OfferAttributes/a:Condition/text()')

    @property
    @first_element
    def offer_listing_id(self):
        return self.xpath('//a:OfferListing/a:OfferListingId/text()')

    @property
    @first_element
    def formatted_price(self):
        return self.xpath('//a:OfferListing/a:Price/a:FormattedPrice/text()')

    @property
    def price(self):
        if self.formatted_price:
            return float(re.sub('[^\d^\.]', '', self.formatted_price))
        return

    @property
    @first_element
    def amount_saved(self):
        return self.xpath('//a:OfferListing/a:AmountSaved/a:FormattedPrice/text()')

    @property
    @first_element
    def percentage_saved(self):
        return self.xpath('//a:OfferListing/a:PercentageSaved/text()')

    @property
    @first_element
    def availability(self):
        return self.xpath('//a:OfferListing/a:Availability')

    @property
    @first_element
    def availability_type(self):
        return self.xpath('//a:OfferListing/a:AvailabilityAttributes/a:AvailabilityType/text()')

    @property
    @first_element
    def availability_minimum_hours(self):
        return self.xpath('//a:OfferListing/a:AvailabilityAttributes/a:MinimumHours/text()')

    @property
    @first_element
    def availability_maximum_hours(self):
        return self.xpath('//a:OfferListing/a:AvailabilityAttributes/a:MaximumHours/text()')

    @property
    @convert_to_bool
    @first_element
    def is_eligible_for_super_saver_shipping(self):
        return self.xpath('//a:OfferListing/a:IsEligibleForSuperSaverShipping/text()')

    @property
    @convert_to_bool
    @first_element
    def is_eligible_for_prime(self):
        return self.xpath('//a:OfferListing/a:IsEligibleForPrime/text()')

    def __repr__(self):
        return '<Offer merchant_name={} price={} prime={}>'.format(self.merchant_name, self.price, self.is_eligible_for_prime)


class Item(BaseLookupWrapper):
    """
    Used to parse out ItemLookupResponse.Items.Item.
    """

    @property
    @first_element
    def asin(self):
        return self.xpath('//a:ASIN/text()')

    @property
    @first_element
    def parent_asin(self):
        return self.xpath('//a:ParentASIN/text()')

    @property
    @convert_to_int
    @first_element
    def sales_rank(self):
        return self.xpath('//a:SalesRank/text()')

    @property
    @first_element
    def formatted_lowest_new_price(self):
        return self.xpath('//a:OfferSummary/a:LowestNewPrice/a:FormattedPrice/text()')

    @property
    def lowest_new_price(self):
        if self.formatted_lowest_new_price:
            return float(re.sub('[^\d^\.]', '', self.formatted_lowest_new_price))
        return

    @property
    @convert_to_int
    @first_element
    def total_new(self):
        return self.xpath('//a:OfferSummary/a:TotalNew/text()')

    @property
    @convert_to_int
    @first_element
    def total_used(self):
        return self.xpath('//a:OfferSummary/a:TotalUsed/text()')

    @property
    @convert_to_int
    @first_element
    def total_collectible(self):
        return self.xpath('//a:OfferSummary/a:TotalCollectible/text()')

    @property
    @convert_to_int
    @first_element
    def total_refurbished(self):
        return self.xpath('//a:OfferSummary/a:TotalRefurbished/text()')

    @property
    @convert_to_int
    @first_element
    def total_offers(self):
        return self.xpath('//a:Offers/a:TotalOffers/text()')

    @property
    @convert_to_int
    @first_element
    def total_offer_pages(self):
        return self.xpath('//a:Offers/a:TotalOfferPages/text()')

    @property
    @first_element
    def more_offers_url(self):
        return self.xpath('//a:Offers/a:MoreOffersUrl/text()')

    @property
    def offers(self):
        return [Offer(x) for x in self.xpath('//a:Offers/a:Offer')]

    def __repr__(self):
        return '<Item asin={} total_offers={} sales_rank={}>'.format(self.asin, self.total_offers, self.sales_rank)

    def __iter__(self):
        return self.offers.__iter__()


class ItemLookup(BaseLookupWrapper):

    @property
    def items(self):
        return [Item(x) for x in self.xpath('//a:Items/a:Item')]

    def __iter__(self):
        return self.items.__iter__()
