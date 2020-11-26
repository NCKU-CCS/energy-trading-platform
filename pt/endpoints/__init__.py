from endpoints.address.resource import AddressResource, AmiResource
from endpoints.user.resource import UserResource, LoginResource, ParticipantResource
from endpoints.news.resource import NewsResource
from endpoints.powerdata.resource import PowerDatasResource
from endpoints.bid.resource import HomePageResource, MatchResultsResource, BidSubmitResource, BidStatusResource
from endpoints.dr.resource import DRBid, DRBidResult
from endpoints.socketio.resource import SocketResource

RESOURCES = {
    "address": AddressResource,
    "amis": AmiResource,
    "user": UserResource,
    "news": NewsResource,
    "power_info": PowerDatasResource,
    "login": LoginResource,
    "participant": ParticipantResource,
    "matchresult": MatchResultsResource,
    "bidsubmit": BidSubmitResource,
    "homepage": HomePageResource,
    "bidstatus": BidStatusResource,
    "DR_bid": DRBid,
    "DR_result": DRBidResult,
    "socketio": SocketResource,
}
