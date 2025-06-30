from ..extensions import ma

# Import schemas after ma is defined
from .user_schema import user_schema, users_schema
from .patient_schema import patient_schema, patients_schema
from .facility_schema import facility_schema, facilities_schema, state_schema, states_schema
from .appointment_schema import drug_pickups_schema, viral_loads_schema
from .performance_schema import trend_data_schema, performance_schema, performance_metrics_schema

__all__ = [
    'ma',
    'user_schema', 'users_schema',
    'patient_schema', 'patients_schema',
    'facility_schema', 'facilities_schema',
    'state_schema', 'states_schema',
    'drug_pickups_schema', 'viral_loads_schema',
    'trend_data_schema', 'performance_schema', 'performance_metrics_schema'
]
