from app.models import CaseManager, State
from app.schemas.case_manager_schema import (
    case_manager_schema, case_managers_schema, 
)
from app import db
from sqlalchemy import func
from sqlalchemy.orm import noload

class CaseManagerService:
    @staticmethod
    def get_all_case_managers(user=None):
        """Get all case managers."""
        query = db.session.query(CaseManager).options(
            noload(CaseManager.assigned_patients),
            noload(CaseManager.performance_metrics),
            noload(CaseManager.drug_pickup_appointments),
            noload(CaseManager.viral_load_appointments)
        )
        # Apply user role-based filtering
        if 'Super Admin' not in user['roles']:
            if 'State' in user['roles']:
                query = query.join(State, State.id == user['state_id']).filter(CaseManager.state == State.name)
            elif 'Admin' in user['roles']:
                query = query.join(State, State.id == user['state_id']).filter(CaseManager.state == State.name)

        return case_managers_schema.dump(query.all())

    @staticmethod
    def update_case_manager(case_manager_id, data):
        case_manager = CaseManager.query.get_or_404(case_manager_id)
        for key, value in data.items():
            setattr(case_manager, key, value)
        db.session.commit()
        return case_manager_schema.dump(case_manager)

    @staticmethod
    def get_case_manager(case_manager_id, user=None):
        """
        Get a single case manager by ID with role-based filtering
        Args:
            case_manager_id: The ID of the case manager to retrieve
            user: Current user with roles and access information
        Returns:
            Dict: Case manager data or None if not found/not authorized
        """
        try:
            query = CaseManager.query

            # Apply user role-based filtering
            if 'Super Admin' not in user['roles']:
                if 'State' in user['roles']:
                    query = query.join(State, State.id == user['state_id']).filter(CaseManager.state == State.name)
                elif 'Admin' in user['roles']:
                    query = query.join(State, State.id == user['state_id']).filter(CaseManager.state == State.name)
            
            case_manager = query.filter(CaseManager.id == case_manager_id).first()
                
            if case_manager:
                return case_manager_schema.dump(case_manager)
            return None

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error fetching case manager: {str(e)}")
            return None
