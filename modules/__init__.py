from .privilege_escalation import check_privilege_escalation
from .persistence import check_persistence
from .credential_harvesting import check_credential_harvesting
from .internal_reconnaissance import check_internal_reconnaissance
from .lateral_movement import check_lateral_movement
from .data_access import check_data_access
from .data_exfiltration import check_data_exfiltration
from .c2_check import check_c2
from .covering_tracks import check_covering_tracks

MODULE_MAP = {
    'privilege_escalation': check_privilege_escalation,
    'persistence': check_persistence,
    'credential_harvesting': check_credential_harvesting,
    'internal_reconnaissance': check_internal_reconnaissance,
    'lateral_movement': check_lateral_movement,
    'data_access': check_data_access,
    'data_exfiltration': check_data_exfiltration,
    'c2_check': check_c2,
    'covering_tracks': check_covering_tracks
}

def execute_module(module_name):
    """Execute a security assessment module"""
    if module_name in MODULE_MAP:
        return MODULE_MAP[module_name]()
    else:
        return {'error': f'Module {module_name} not found'}
