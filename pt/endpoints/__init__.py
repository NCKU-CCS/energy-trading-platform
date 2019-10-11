from endpoints.address.resource import AddressResource, AmiResource
from endpoints.user.resource import UserResource


RESOURCES = {
    'address': AddressResource,
    'amis': AmiResource,
    'user': UserResource
    }
