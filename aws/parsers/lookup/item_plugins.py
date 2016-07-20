"""
This module is used for creating a ItemLookup response parser from amazon's AWS API.
"""

from base import BaseLookupWrapper, first_element, parse_bool, parse_float, parse_int


class Item(BaseLookupWrapper):

    @property
    @first_element
    def asin(self):
        return self.xpath('./a:ASIN/text()')

    @property
    @first_element
    def parent_asin(self):
        return self.xpath('./a:ParentASIN/text()')


class Offers(BaseLookupWrapper):

    class Offer(BaseLookupWrapper):

        class Listing(BaseLookupWrapper):

            @property
            @first_element
            def offer_listing_id(self):
                return self.xpath('./a:OfferListingId/text()')

            @property
            @parse_float
            @first_element
            def price(self):
                return self.xpath('./a:Price/a:FormattedPrice/text()')

            @property
            @parse_float
            @first_element
            def amount_saved(self):
                return self.xpath('./a:AmountSaved/a:FormattedPrice/text()')

            @property
            @parse_int
            @first_element
            def percentage_saved(self):
                return self.xpath('./a:PercentageSaved/text()')

            # ToDo: AvailibilityAttributes

            @property
            @parse_bool
            @first_element
            def is_eligible_for_super_saver_shipping(self):
                return self.xpath('./a:IsEligibleForSuperSaverShipping/text()')

            @property
            @parse_bool
            @first_element
            def is_eligible_for_prime(self):
                return self.xpath('./a:IsEligibleForPrime/text()')

            def __repr__(self):
                return '<OfferListing price={} is_eligible_for_prime={}>'.format(self.price, self.is_eligible_for_prime)

        @property
        @first_element
        def condition(self):
            return self.xpath('./a:OfferAttributes/a:Condition/text()')

        @property
        def _offer_listings(self):
            return [self.Listing(x) for x in self.xpath('.//a:OfferListing')]

        @property
        def offer_listings(self):
            """
            Deprecated since offer listings element will always only contain the
            lowest priced/buy box seller.
            :return:
            """
            import warnings
            warnings.warn('offer_listings is no longer useful since only one offer listing is returned. Use offer_listing instead')
            return self._offer_listings

        @property
        def offer_listing(self):
            if not self._offer_listings:
                return None
            return self._offer_listings[0]

        @property
        @first_element
        def merchant_name(self):
            return self.xpath('./a:Merchant/a:Name/text()')

        def __repr__(self):
            return '<Offer merchant_name={} condition={} offer_listings={}>'.format(self.merchant_name, self.condition, self.offer_listings)

    @property
    @parse_int
    @first_element
    def total_offers(self):
        return self.xpath('./a:Offers/a:TotalOffers/text()')

    @property
    @parse_int
    @first_element
    def total_offer_pages(self):
        return self.xpath('./a:Offers/a:TotalOfferPages/text()')

    @property
    @first_element
    def more_offers_url(self):
        return self.xpath('./a:Offers/a:MoreOffersUrl/text()')

    @property
    def offers(self):
        return [self.Offer(x) for x in self.xpath('.//a:Offer')]

    def __repr__(self):
        return '<Offers total_offers={} offers={}>'.format(self.total_offers, self.offers)


class OfferSummary(BaseLookupWrapper):
    """
    Used to wrap the elements which are returned by the OfferSummary ResponseGroup in the ItemLookup response.

    http://docs.aws.amazon.com/AWSECommerceService/latest/DG/RG_OfferSummary.html
    """

    @property
    @parse_float
    @first_element
    def lowest_new_price(self):
        return self.xpath('./a:OfferSummary/a:LowestNewPrice/a:FormattedPrice/text()')

    @property
    @parse_float
    @first_element
    def lowest_used_price(self):
        return self.xpath('./a:OfferSummary/a:LowestUsedPrice/a:FormattedPrice/text()')

    @property
    @parse_float
    @first_element
    def lowest_collectible_price(self):
        return self.xpath('./a:OfferSummary/a:LowestCollectiblePrice/a:FormattedPrice/text()')

    @property
    @parse_float
    @first_element
    def lowest_refurbished_price(self):
        return self.xpath('./a:OfferSummary/a:LowestRefurbishedPrice/a:FormattedPrice/text()')

    @property
    @parse_int
    @first_element
    def total_new(self):
        return self.xpath('./a:OfferSummary/a:TotalNew/text()')

    @property
    @parse_int
    @first_element
    def total_used(self):
        return self.xpath('./a:OfferSummary/a:TotalUsed/text()')

    @property
    @parse_int
    @first_element
    def total_collectible(self):
        return self.xpath('./a:OfferSummary/a:TotalCollectible/text()')

    @property
    @parse_int
    @first_element
    def total_refurbished(self):
        return self.xpath('./a:OfferSummary/a:TotalRefurbished/text()')


class SalesRank(BaseLookupWrapper):
    """
    Used to wrap the elements which are returned by the SalesRank ResponseGroup in the ItemLookup response.

    http://docs.aws.amazon.com/AWSECommerceService/latest/DG/RG_SalesRank.html
    """

    @property
    @parse_int
    @first_element
    def sales_rank(self):
        return self.xpath('./a:SalesRank/text()')


class ItemLinks(BaseLookupWrapper):

    @property
    @first_element
    def detail_page_url(self):
        return self.xpath('./a:DetailPageURL/text()')

    @property
    def item_links(self):
        item_links = [BaseLookupWrapper(x) for x in self.xpath('./a:ItemLinks//a:ItemLink')]
        return [(x.xpath('./a:Description/text()')[0].strip(), x.xpath('./a:URL/text()')[0].strip()) for x in item_links]


class BaseImageWrapper(BaseLookupWrapper):
    """
    Used to wrap any element which contains image data. (height, width, url)
    """

    def mk_img_from_elem(self, elem):
        elem = [elem]
        return self._mk_img(elems=elem)

    def mk_img_from_xpath(self, xpath):
        return self._mk_img(xpath=xpath)

    def _mk_img(self, xpath=None, elems=None):
        # elem should at least contain one element even if it's None to prevent IndexErrors
        # on the next line.
        elem = elems or self.xpath(xpath) or [None]
        return self.Img(elem[0])

    class Img(BaseLookupWrapper):
        @property
        @first_element
        def url(self):
            return self.xpath('./a:URL/text()')

        @property
        @parse_int
        @first_element
        def height(self):
            return self.xpath('./a:Height/text()')

        @property
        @parse_int
        @first_element
        def width(self):
            return self.xpath('./a:Width/text()')

        def __repr__(self):
            return '<ImageElement url={} height={} width={}>'.format(self.url, self.height, self.width)


class Images(BaseImageWrapper):
    """
    Used to wrap the elements which are returned by the Images ResponseGroup in the ItemLookup response.

    http://docs.aws.amazon.com/AWSECommerceService/latest/DG/RG_Images.html
    """

    class ImageSet(BaseImageWrapper):
        """
        Used to wrap an ImageSet element for parsing.
        """

        @property
        def swatch_image(self):
            return self.mk_img_from_xpath('./a:SwatchImage')

        @property
        def small_image(self):
            return self.mk_img_from_xpath('./a:SmallImage')

        @property
        def thumbnail_image(self):
            return self.mk_img_from_xpath('./a:ThumbnailImage')

        @property
        def tiny_image(self):
            return self.mk_img_from_xpath('./a:TinyImage')

        @property
        def medium_image(self):
            return self.mk_img_from_xpath('./a:MediumImage')

        @property
        def large_image(self):
            return self.mk_img_from_xpath('./a:LargeImage')

    @property
    def small_image(self):
        return self.mk_img_from_xpath('./a:SmallImage')

    @property
    def medium_image(self):
        return self.mk_img_from_xpath('./a:MediumImage')

    @property
    def large_image(self):
        return self.mk_img_from_xpath('./a:LargeImage')

    @property
    def image_set_variant(self):
        image_set_element_list = self.xpath('./a:ImageSets/a:ImageSet[@Category="variant"]')
        if not image_set_element_list:
            return self.ImageSet(None)
        return self.ImageSet(image_set_element_list[0])

    @property
    def image_set_primary(self):
        image_set_element_list = self.xpath('./a:ImageSets/a:ImageSet[@Category="primary"]')
        if not image_set_element_list:
            return self.ImageSet(None)
        return self.ImageSet(image_set_element_list[0])


class BaseDimensionsWrapper(BaseLookupWrapper):
    """
    Element wrapper which is used to parse out dimensions from elements which contain height/width/length/weight.
    """

    def mk_dimens_from_elem(self, elem):
        elem = [elem]
        return self._mk_dimens(elems=elem)

    def mk_dimens_from_xpath(self, xpath):
        return self._mk_dimens(xpath=xpath)

    def _mk_dimens(self, xpath=None, elems=None):
        elem = elems or self.xpath(xpath)
        return self.Dimens(elem[0] if elem else None)

    class Dimens(BaseLookupWrapper):

        @property
        @parse_int
        @first_element
        def height(self):
            return self.xpath('./a:Height/text()')

        @property
        @parse_int
        @first_element
        def length(self):
            return self.xpath('./a:Length/text()')

        @property
        @parse_int
        @first_element
        def width(self):
            return self.xpath('./a:Width/text()')

        @property
        @parse_int
        @first_element
        def weight(self):
            return self.xpath('./a:Weight/text()')

        def __repr__(self):
            return '<DimensionsElement length={} height={} width={}>'.format(self.length, self.height, self.width)


class ItemAttributes(BaseDimensionsWrapper):
    """
    Used to wrap the elements which are returned by the ItemAttributes ResponseGroup in the ItemLookup response.

    http://docs.aws.amazon.com/AWSECommerceService/latest/DG/RG_ItemAttributes.html
    """
    
    @property
    @first_element
    def actor(self):  # ToDo: test
        return self.xpath('./a:ItemAttributes/a:Actor/text()')
    
    @property
    @first_element
    def artist(self):  # ToDo: test
        return self.xpath('./a:ItemAttributes/a:Artist/text()')
    
    @property
    @first_element
    def aspect_ratio(self):  # ToDo: test
        return self.xpath('./a:ItemAttributes/a:AspectRatio/text()')

    @property
    @first_element
    def audience_rating(self):  # ToDo: test
        return self.xpath('./a:ItemAttributes/a:AudienceRating/text()')

    @property
    @first_element
    def audio_format(self):  # ToDo: test
        return self.xpath('./a:ItemAttributes/a:AudioFormat/text()')

    @property
    @first_element
    def author(self):  # ToDo: test
        return self.xpath('./a:ItemAttributes/a:Author/text()')

    @property
    @first_element
    def binding(self):
        return self.xpath('./a:ItemAttributes/a:Binding/text()')

    @property
    @first_element
    def brand(self):
        return self.xpath('./a:ItemAttributes/a:Brand/text()')

    @property
    @first_element
    def category(self):  # ToDo: test
        return self.xpath('./a:ItemAttributes/a:Category/text()')

    @property
    @first_element
    def cero_age_rating(self):  # ToDo: test
        return self.xpath('./a:ItemAttributes/a:CEROAgeRating/text()')

    @property
    @first_element
    def clothing_size(self):  # ToDo: test
        return self.xpath('./a:ItemAttributes/a:ClothingSize/text()')

    @property
    @first_element
    def color(self):  # ToDo: test
        return self.xpath('./a:ItemAttributes/a:Color/text()')

    # ToDo: Creator/Role

    @property
    def catalog_number_list(self):
        return [x.strip() for x in self.xpath('./a:ItemAttributes/a:CatalogNumberList//text()') if x.strip()]

    @property
    @first_element
    def ean(self):
        return self.xpath('./a:ItemAttributes/a:EAN/text()')

    @property
    def ean_list(self):
        return [x.strip() for x in self.xpath('./a:ItemAttributes/a:EANList/a:EANListElement//text()') if x.strip()]

    @property
    def features(self):
        return [x.strip() for x in self.xpath('./a:ItemAttributes//a:Feature/text()') if x.strip()]

    @property
    @parse_bool
    @first_element
    def is_adult_product(self):
        return self.xpath('./a:ItemAttributes/a:IsAdultProduct/text()')

    @property
    def item_dimensions(self):
        return self.mk_dimens_from_xpath('./a:ItemAttributes/a:ItemDimensions')

    @property
    @first_element
    def label(self):
        return self.xpath('./a:ItemAttributes/a:Label/text()')

    @property
    @parse_float
    @first_element
    def list_price(self):
        return self.xpath('./a:ItemAttributes/a:ListPrice/a:FormattedPrice/text()')

    @property
    @first_element
    def manufacturer(self):
        return self.xpath('./a:ItemAttributes/a:Manufacturer/text()')

    @property
    @first_element
    def model(self):
        return self.xpath('./a:ItemAttributes/a:Model/text()')

    @property
    @first_element
    def mpn(self):
        return self.xpath('./a:ItemAttributes/a:MPN/text()')

    @property
    @parse_int
    @first_element
    def number_of_items(self):
        return self.xpath('./a:ItemAttributes/a:NumberOfItems/text()')

    @property
    def package_dimensions(self):
        return self.mk_dimens_from_xpath('./a:ItemAttributes/a:PackageDimensions')

    @property
    @parse_int
    @first_element
    def package_quantity(self):
        return self.xpath('./a:ItemAttributes/a:PackageQuantity/text()')

    @property
    @first_element
    def part_number(self):
        return self.xpath('./a:ItemAttributes/a:PartNumber/text()')

    @property
    @first_element
    def product_group(self):
        return self.xpath('./a:ItemAttributes/a:ProductGroup/text()')

    @property
    @first_element
    def product_type_name(self):
        return self.xpath('./a:ItemAttributes/a:ProductTypeName/text()')

    @property
    @first_element
    def publication_date(self):
        return self.xpath('./a:ItemAttributes/a:PublicationDate/text()')

    @property
    @first_element
    def publisher(self):
        return self.xpath('./a:ItemAttributes/a:Publisher/text()')

    @property
    @first_element
    def release_date(self):
        return self.xpath('./a:ItemAttributes/a:ReleaseDate/text()')

    @property
    @first_element
    def studio(self):
        return self.xpath('./a:ItemAttributes/a:Studio/text()')

    @property
    @first_element
    def title(self):
        return self.xpath('./a:ItemAttributes/a:Title/text()')

    @property
    @first_element
    def upc(self):
        return self.xpath('./a:ItemAttributes/a:UPC/text()')

    @property
    def upc_list(self):
        return [x.strip() for x in self.xpath('./a:ItemAttributes/a:UPCList//a:UPCListElement/text()') if x.strip()]


class BrowseNodes(BaseLookupWrapper):

    class BrowseNode(BaseLookupWrapper):

        @property
        @first_element
        def browse_node_id(self):
            return self.xpath('./a:BrowseNodeId/text()')

        @property
        @first_element
        def name(self):
            return self.xpath('./a:Name/text()')

        @property
        @first_element
        def _next_ancestor(self):
            return self.xpath('./a:Ancestors/a:BrowseNode')

        @property
        def has_ancestor(self):
            return self._next_ancestor is not None

        @property
        def next_ancestor(self):
            return BrowseNodes.BrowseNode(self._next_ancestor)

        def __repr__(self):
            return '<BrowseNode name={} browse_node_id={}>'.format(self.name, self.browse_node_id)

    @property
    def browse_nodes(self):
        l = []
        browse_node = self.first_browse_node
        l.append(browse_node)
        while browse_node.has_ancestor:
            browse_node = browse_node.next_ancestor
            l.append(browse_node)
        return l

    @property
    @first_element
    def _first_browse_node(self):
        return self.xpath('./a:BrowseNodes/a:BrowseNode')

    @property
    def first_browse_node(self):
        return self.BrowseNode(self._first_browse_node)


# ToDo: EditorialReview

# ToDo: ItemIds

# ToDo: Accessories

# ToDo: Reviews

# ToDo: Similarities

# ToDo: Tracks

# ToDo: PromotionSummary

# ToDo: RelatedItems

# ToDo: VariationImages

# ToDo: Variations


class Small(ItemLinks, ItemAttributes):
    pass


class Medium(Small, OfferSummary, SalesRank, Images):
    pass


class Large(Medium, Offers, BrowseNodes):
    pass


class OfferFull(Offers, OfferSummary):
    """
    Dont mix with Large. It will cause an MRO Error.

    Large already contains the Offers class which contains all response groups returned
    by OfferFull. Offer full should only be used if you're Requesting OfferFull in conjuction
    with anything other than Large.

    If requesting Large and OfferFull response groups, just use Large.
    """
    pass
