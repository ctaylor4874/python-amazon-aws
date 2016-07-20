import os

from lxml import etree

from aws.parsers import Large, Item, ItemLookupResponse, OfferFull, Small
from aws import Lookup


if __name__ == '__main__':

    class MyItem(Item, Small):
        pass

    l = Lookup(os.getenv('AWS_ASSOCIATE_TAG'), os.getenv('AWS_ACCESS_KEY'), os.getenv('AWS_SECRET_KEY'))
    data = l.item_lookup(item_ids=('B00FRIQEDW', 'B0036DEALS', 'B00FB6O9I2', 'B00E4MQKC2', 'B00D6N8U9G', 'B00CMT632Q', 'B00BXTKL1A', 'B00BMJH9XE', 'B00BV1P6GK', 'B00BV1P48A'),  Condition='New')
    ilr = ItemLookupResponse(etree.fromstring(data), MyItem)
    for err in ilr.items.request.errors:
        err.raise_for_error()
    for itm in ilr.items.item_list():
        item = itm
        """:type item: MyItem"""
        print '-----------------------------------------------------------'
        print 'asin:                    ', item.asin
        print 'itemlinks:               ', item.item_links
        print 'brand:                   ', item.brand
        print 'munfacturer item #:      ', item.model
        print 'manufacturer part #:     ', item.part_number
        print 'upc:                     ', item.upc
        print 'product group:           ', item.product_group
        print 'title:                   ', item.title
