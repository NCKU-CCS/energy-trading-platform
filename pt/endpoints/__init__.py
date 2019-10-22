from endpoints.address.resource import AddressResource, AmiResource
from endpoints.user.resource import UserResource, LoginResource, ParticipantResource
from endpoints.news.resource import NewsResource
from endpoints.data.resource import DatasResource
from endpoints.bid.resource import BidsResource

RESOURCES = {
    'address': AddressResource,
    'amis': AmiResource,
    'user': UserResource,
    'news': NewsResource,
    'power_info': DatasResource,
    'login': LoginResource,
    'participant': ParticipantResource,
    'bids': BidsResource,
}
