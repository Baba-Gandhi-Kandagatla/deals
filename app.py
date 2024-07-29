from flask import Flask, request, jsonify
from paapi5_python_sdk.api.default_api import DefaultApi
from paapi5_python_sdk.models.partner_type import PartnerType
from paapi5_python_sdk.models.search_items_request import SearchItemsRequest
from paapi5_python_sdk.models.search_items_resource import SearchItemsResource
from paapi5_python_sdk.rest import ApiException
from dotenv import load_dotenv
import os
app = Flask(__name__)
load_dotenv()
# Your Amazon credentials
ACCESS_KEY = os.getenv("ACCESS_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")
PARTNER_TAG = os.getenv("PARTNER_TAG")
HOST = "webservices.amazon.in"
REGION = "eu-west-1"

# API declaration
default_api = DefaultApi(
    access_key=ACCESS_KEY, secret_key=SECRET_KEY, host=HOST, region=REGION
)


@app.route('/search', methods=['GET'])
def search_items():
    # Get query parameters
    keywords = request.args.get('keywords', 'deals')
    search_index = request.args.get('search_index', 'All')
    item_count = int(request.args.get('item_count', 25))

    # Choose resources you want from SearchItemsResource enum
    search_items_resource = [
  "BrowseNodeInfo.BrowseNodes",
  "BrowseNodeInfo.BrowseNodes.Ancestor",
  "BrowseNodeInfo.BrowseNodes.SalesRank",
  "BrowseNodeInfo.WebsiteSalesRank",
  "Images.Primary.Small",
  "Images.Primary.Medium",
  "Images.Primary.Large",
  "Images.Primary.HighRes",
  "Images.Variants.Small",
  "Images.Variants.Medium",
  "Images.Variants.Large",
  "Images.Variants.HighRes",
  "ItemInfo.Features",
  "ItemInfo.ProductInfo",
  "ItemInfo.Title",
  "ItemInfo.TradeInInfo",
  "Offers.Listings.Availability.MaxOrderQuantity",
  "Offers.Listings.Availability.Message",
  "Offers.Listings.Availability.MinOrderQuantity",
  "Offers.Listings.Availability.Type",
  "Offers.Listings.DeliveryInfo.IsAmazonFulfilled",
  "Offers.Listings.DeliveryInfo.IsFreeShippingEligible",
  "Offers.Listings.DeliveryInfo.IsPrimeEligible",
  "Offers.Listings.DeliveryInfo.ShippingCharges",
  "Offers.Listings.IsBuyBoxWinner",
  "Offers.Listings.LoyaltyPoints.Points",
  "Offers.Listings.MerchantInfo",
  "Offers.Listings.Price",
  "Offers.Listings.ProgramEligibility.IsPrimeExclusive",
  "Offers.Listings.ProgramEligibility.IsPrimePantry",
  "Offers.Listings.Promotions",
  "Offers.Listings.SavingBasis",
  "Offers.Summaries.HighestPrice",
  "Offers.Summaries.LowestPrice",
  "Offers.Summaries.OfferCount",
  "SearchRefinements"
 ]

    # Forming request
    try:
        search_items_request = SearchItemsRequest(
            partner_tag=PARTNER_TAG,
            partner_type=PartnerType.ASSOCIATES,
            keywords=keywords,
            search_index=search_index,
            item_count=item_count,
            resources=search_items_resource,
        )
    except ValueError as exception:
        return jsonify({"error": f"Error in forming SearchItemsRequest: {exception}"}), 400

    try:
        # Sending request
        response = default_api.search_items(search_items_request)
        
        # Parse response
        items = []
        if response.search_result is not None:
            for item in response.search_result.items:
                item_info = {
                    "DetailPageURL":item.detail_page_url,
                    "ASIN": item.asin,
                    "Title": item.item_info.title.display_value if item.item_info and item.item_info.title else None,
                    "Features": item.item_info.features.display_values if item.item_info and item.item_info.features else [],
                    "ProductInfo": {
                        "Height": item.item_info.product_info.item_dimensions.height.display_value if item.item_info and item.item_info.product_info and item.item_info.product_info.item_dimensions and item.item_info.product_info.item_dimensions.height else None,
                        "Length": item.item_info.product_info.item_dimensions.length.display_value if item.item_info and item.item_info.product_info and item.item_info.product_info.item_dimensions and item.item_info.product_info.item_dimensions.length else None,
                        "Width": item.item_info.product_info.item_dimensions.width.display_value if item.item_info and item.item_info.product_info and item.item_info.product_info.item_dimensions and item.item_info.product_info.item_dimensions.width else None,
                        "Weight": item.item_info.product_info.item_dimensions.weight.display_value if item.item_info and item.item_info.product_info and item.item_info.product_info.item_dimensions and item.item_info.product_info.item_dimensions.weight else None,
                    },
                    "Images": {
                        "Primary": {
                            "Small": item.images.primary.small.url if item.images and item.images.primary and item.images.primary.small else None,
                            "Medium": item.images.primary.medium.url if item.images and item.images.primary and item.images.primary.medium else None,
                            "Large": item.images.primary.large.url if item.images and item.images.primary and item.images.primary.large else None,
                        },
                        "Variants": [
                            {
                                "Small": variant.small.url if variant and variant.small else None,
                                "Medium": variant.medium.url if variant and variant.medium else None,
                                "Large": variant.large.url if variant and variant.large else None,
                            } for variant in item.images.variants if item.images and item.images.variants
                        ],
                    },
                    "BrowseNodes": [
                        {
                            "ID": node.id,
                            "DisplayName": node.display_name,
                            "Ancestor": {
                                "ID": node.ancestor.id if node.ancestor else None,
                                "DisplayName": node.ancestor.display_name if node.ancestor else None
                            } if node.ancestor else None,
                            "SalesRank": node.sales_rank if node.sales_rank else None
                        } for node in item.browse_node_info.browse_nodes if item.browse_node_info and item.browse_node_info.browse_nodes
                    ],
                    "Offers": [
                        {
                            "Price": offer.price.amount if offer and offer.price else None,
                            "Currency": offer.price.currency if offer and offer.price else None,
                            "Availability": {
                                "Message": offer.availability.message if offer and offer.availability else None,
                                "Type": offer.availability.type if offer and offer.availability else None,
                                "MinOrderQuantity": offer.availability.min_order_quantity if offer and offer.availability else None,
                                "MaxOrderQuantity": offer.availability.max_order_quantity if offer and offer.availability else None,
                            } if offer.availability else None,
                            "DeliveryInfo": {
                                "IsAmazonFulfilled": offer.delivery_info.is_amazon_fulfilled if offer and offer.delivery_info else None,
                                "IsFreeShippingEligible": offer.delivery_info.is_free_shipping_eligible if offer and offer.delivery_info else None,
                                "IsPrimeEligible": offer.delivery_info.is_prime_eligible if offer and offer.delivery_info else None,
                            } if offer.delivery_info else None,
                        } for offer in item.offers.listings if item.offers and item.offers.listings
                    ]
                }
                items.append(item_info)
        
        if response.errors is not None:
            return jsonify({"errors": [{"code": error.code, "message": error.message} for error in response.errors]}), 400
        
        return jsonify({"items": items})

    except ApiException as exception:
        return jsonify({
            "error": "Error calling PA-API 5.0!",
            "status_code": exception.status,
            "errors": exception.body,
            "request_id": exception.headers["x-amzn-RequestId"]
        }), 500

    except Exception as exception:
        return jsonify({"error": str(exception)}), 500


if __name__ == '__main__':
    app.run(debug=True)
