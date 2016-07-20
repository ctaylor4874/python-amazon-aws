import os

from lxml import etree

from parsers.lookup import Small, Medium, Item, ItemLookupResponse
from aws_ import Lookup


if __name__ == '__main__':

    class MyItem(Item, Medium):
        pass

    l = Lookup(os.getenv('AWS_ASSOCIATE_TAG'), os.getenv('AWS_ACCESS_KEY'), os.getenv('AWS_SECRET_KEY'))
    data = l.item_lookup(item_ids=('B0036DEALS', 'B00K7DMEJ0'), response_groups=('Medium',))
    ilr = ItemLookupResponse(etree.fromstring(data), MyItem)
    for itm in ilr.items.item_list():
        item = itm
        """:type item: MyItem"""
        print '------------------'
        print item.asin
        print item.manufacturer
        print item.item_links
        print item.lowest_new_price
        print item.list_price
        print item.item_dimensions
