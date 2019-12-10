from endpoints.address.resource import AddressResource, AmiResource
from endpoints.user.resource import UserResource, LoginResource, ParticipantResource
from endpoints.news.resource import NewsResource
from endpoints.powerdata.resource import PowerDatasResource
from endpoints.bid.resource import MatchResultsResource, BidSubmitResource


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
}
