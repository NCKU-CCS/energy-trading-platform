from models.models import db, FieldModel, HistoryModel, UploaderModel
from generate_address import get_addresses

db.create_all()


def get_address(name, time):
    field = FieldModel.find(name, time)
    if field:
        return field.address
    if not FieldModel.find_by_name(name):
        # need to add field into database
        FieldModel.add_field(FieldModel(name, 'x', time))
    # Generate address for all fields in database
    renew_address(time)
    field = FieldModel.find(name, time)
    return field.address


def renew_address(time):
    address = get_addresses(int(time.strftime("%s")), FieldModel.query.count())
    for field in FieldModel.query.all():
        field.address = str(address[field.id - 1])
        field.time = time
        FieldModel.update_field(field)
        # Add to history table
        if not HistoryModel.find(field.name, field.time):
            HistoryModel.add_field(HistoryModel(field.name, field.address, field.time))


def check_uploader(tag):
    uploader = UploaderModel.find_by_tag(tag)
    if uploader:
        return uploader
    return None
