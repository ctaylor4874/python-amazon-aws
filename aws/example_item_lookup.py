import os

from lxml import etree

from parsers.lookup import Large, Medium, Item, ItemLookupResponse
from aws_ import Lookup


if __name__ == '__main__':

    class MyItem(Item, Large):
        pass

    l = Lookup(os.getenv('AWS_ASSOCIATE_TAG'), os.getenv('AWS_ACCESS_KEY'), os.getenv('AWS_SECRET_KEY'))
    data = l.item_lookup(item_ids=('B00FRIQEDW', 'B0036DEALS'), response_groups=('Large',), Condition='New')
    ilr = ItemLookupResponse(etree.fromstring(data), MyItem)
    for err in ilr.items.request.errors:
        err.raise_for_error()
    for itm in ilr.items.item_list():
        item = itm
        """:type item: MyItem"""
        print '-----------------------------------------------------------'
        print 'asin:                ', item.asin
        print 'bb/lowest price:     ', item.lowest_new_price
        print 'rank:                ', item.sales_rank
        print 'offers:              ', item.total_new
        print 'brand:               ', item.brand
        print 'munfacturer item #:  ', item.model
        print 'manufacturer part #: ', item.part_number
        print 'upc:                 ', item.upc
        print 'product group:       ', item.product_group
        print 'title:               ', item.title
        print 'image url:           ', item.large_image.url
