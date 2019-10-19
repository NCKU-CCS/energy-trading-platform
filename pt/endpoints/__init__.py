from endpoints.address.resource import AddressResource, AmiResource
from endpoints.user.resource import UserResource, LoginResource, ParticipantResource
from endpoints.news.resource import NewsResource
from endpoints.data.resource import DatasResource

RESOURCES = {
    'address': AddressResource,
    'amis': AmiResource,
    'user': UserResource,
    'news': NewsResource,
    'datas': DatasResource,
    'login': LoginResource,
    'participant': ParticipantResource
    }
