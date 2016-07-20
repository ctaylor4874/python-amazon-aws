import os

from lxml import etree

from parsers.lookup import Large, Item, ItemLookupResponse, OfferFull
from aws_ import Lookup


if __name__ == '__main__':

    class MyItem(Item, Large):
        pass

    l = Lookup(os.getenv('AWS_ASSOCIATE_TAG'), os.getenv('AWS_ACCESS_KEY'), os.getenv('AWS_SECRET_KEY'))
    data = l.item_lookup(item_ids=('B00FRIQEDW', 'B0036DEALS', 'B00FB6O9I2', 'B00E4MQKC2', 'B00D6N8U9G', 'B00CMT632Q', 'B00BXTKL1A', 'B00BMJH9XE', 'B00BV1P6GK', 'B00BV1P48A'), response_groups=('OfferFull', 'Large'), Condition='New')
    ilr = ItemLookupResponse(etree.fromstring(data), MyItem)
    for err in ilr.items.request.errors:
        err.raise_for_error()
    for itm in ilr.items.item_list():
        item = itm
        """:type item: MyItem"""
        print '-----------------------------------------------------------'
        for offer in item.offers:
            print offer.condition + " Offer Is Prime:      ", offer.offer_listing.is_eligible_for_prime
            print offer.condition + " Offer Seller Name:   ", offer.merchant_name
        print 'asin:                    ', item.asin
        print 'bb/lowest price:         ', item.lowest_new_price
        print 'rank:                    ', item.sales_rank
        print 'offers:                  ', item.total_new
        print 'brand:                   ', item.brand
        print 'munfacturer item #:      ', item.model
        print 'manufacturer part #:     ', item.part_number
        print 'upc:                     ', item.upc
        print 'product group:           ', item.product_group
        print 'title:                   ', item.title
        print 'image url:               ', item.large_image.url
        print 'categories:              ', " > ".join([x.name for x in reversed(item.browse_nodes)])
