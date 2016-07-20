# Description

Contains wrappers for the amazon AWS API as well as parsers to parse out
and convert the response from the API request into python objects.

# Notes

* Only the ItemLookup api operation is available right now.
* Some response groups still need to have the python object wrapper/parser created for them.
* Some response groups are still missing some attributes which are returned back by the API operation.
* This library is still very heavy in development.

# Usage 

```python
### Requesting ###

from aws import Lookup

associate_tag = "<your associate tag>"
access_key = "<your access key>"
secret_key = "<your secret key>"
marketplace = "<your marketplace>"  # (optional) defaults to "webservices.amazon.com"

lookup = Lookup(associate_tag, access_key, secret_key, marketplace=marketplace)
# contains the xml response from the API operation
# when no response group is supplied then the default response group is "Small" as shown in the docs (http://docs.aws.amazon.com/AWSECommerceService/latest/DG/ItemLookup.html).
response_content = lookup.item_lookup(item_ids=('TEST_ASIN',))

### Parsing ###

from lxml import etree

from aws.parsers import ItemLookupResponse, Small, Item

# Create a response group parser object by using the mixins available from aws.parsers
# The `Small` object contains everything relevent to the Small API response group and the `Item` object contains only asin and parent asin for the returned item.
class MyParser(Small, Item):
    pass

# Note that we're not passing an instance of MyParser to the ItemLookupResponse, We're just passing the object.
tree = etree.fromstring(response_content)
item_lookup_response = ItemLookupResponse(tree, MyParser)

# Check if there were any errors. If you'd like, you can just print the err.
for err in item_lookup_response.items.request.errors:
    err.raise_for_error()

for item in item_lookup_response.items.item_list():
    print item.asin
    print item.product_group
    print item.manufacturer
    print item.title
    print item.item_links
    print item.detail_page_url
```

# Installation

Clone the repository locally.

`pip install -e /path/to/python-amazon-aws/`
