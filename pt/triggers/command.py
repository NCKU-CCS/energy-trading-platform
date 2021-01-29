from flask_script import Manager

from triggers.bidsubmit import Bid
from triggers.dr import DRAccepted, DRDenied
from triggers.execution_settlement import ExecSettlement, DoneSettlement, Settlement
from triggers.match import Match


def init_manager():
    manager = Manager(usage="Perform platform triggers")
    manager.add_command("bidsubmit", Bid)
    manager.add_command("accepted_dr_upload", DRAccepted)
    manager.add_command("denied_dr_upload", DRDenied)
    manager.add_command("execution_settlement", ExecSettlement)
    manager.add_command("done_settlement", DoneSettlement)
    manager.add_command("settlement", Settlement)
    manager.add_command("match", Match)
    return manager
