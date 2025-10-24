from app.models import CMT, CaseManager, Patient, State, CaseManagerPerformance
from app.schemas.cmt_schema import cmt_schema, cmts_schema
from app import db
from sqlalchemy import func, and_, distinct
from datetime import datetime

class CMTService:
    @staticmethod
    def get_all_cmt(user=None):
        """Get all CMTs with case managers and patient counts."""
        # Start with base CMT query
        query = db.session.query(CMT)
        
        if 'Super Admin' not in user['roles']:
                if 'Admin' in user['roles'] or 'State' in user['roles']:
                    query = query.join(
                        State,
                        State.name == CMT.state
                    ).filter(State.id == user['state_id'])

        cmts = query.all()
        result = []

        for cmt in cmts:
            # Get case managers for this CMT that match both state and facility
            case_managers = db.session.query(CaseManager).filter(
                and_(
                    CaseManager.cmt == cmt.name,
                    CaseManager.state == cmt.state,
                    CaseManager.facilities == cmt.facility_name
                )
            ).all()

            # Get patient count for this CMT's case managers
            total_patient_count = 0
            for case_manager in case_managers:
                patient_count = db.session.query(Patient).filter(
                    and_(
                        # CaseManager.cmt == cmt.name,
                        # CaseManager.state == cmt.state,
                        # CaseManager.facilities == cmt.facility_name
                        Patient.case_manager_id == case_manager.cm_id
                    )).count()
                total_patient_count += patient_count

            # Create the CMT dict with additional data
            cmt_data = cmt_schema.dump(cmt)
            cmt_data['case_managers'] = [
                {
                    'id': cm.id,
                    'fullname': cm.fullname,
                    'role': cm.role,
                    'state': cm.state,
                    'facilities': cm.facilities,
                    'created_at': cm.created_at.isoformat() if cm.created_at else None
                }
                for cm in case_managers
            ]
            cmt_data['patient_count'] = total_patient_count
            result.append(cmt_data)

        return result    
    
    @staticmethod
    def create_cmt(data):
        try:
            if not CMTService._validate_cmt_data(data):
                raise ValueError("Invalid CMT data")

            cmt = CMT(
                name=data['name'],
                state=data['state'],
                facility_name=data['facility_name'],
            )
            db.session.add(cmt)
            db.session.commit()
            return cmt_schema.dump(cmt)
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def _validate_cmt_data(data):
        required = ['name', 'state', 'facility_name']
        return all(key in data for key in required)

    @staticmethod
    def get_single_cmt(cmt_id, user=None):
        """
        Get a single CMT with all its details and performance metrics
        Args:
            cmt_id: The ID of the CMT to retrieve
            user: The current user with role and access information
        Returns:
            dict: CMT details including case managers, patient count and performance metrics
        """
        try:
            # Get the CMT
            query = db.session.query(CMT).filter(CMT.id == cmt_id)
            
            # Apply user role filtering
            if 'Super Admin' not in user['roles']:
                if 'Admin' in user['roles'] or 'State' in user['roles']:
                    query = query.join(
                        State,
                        State.name == CMT.state
                    ).filter(State.id == user['state_id'])

            cmt = query.first()
            if not cmt:
                return None

            # Get case managers for this CMT
            case_managers = db.session.query(CaseManager).filter(
                and_(
                    CaseManager.cmt == cmt.name,
                    CaseManager.state == cmt.state,
                    CaseManager.facilities == cmt.facility_name
                )
            ).all()

            print(f"Case managers for CMT {cmt.name}: {[cm.id for cm in case_managers]}")

            # Get patient count
            total_patient_count = 0
            for case_manager in case_managers:
                patient_count = db.session.query(Patient).filter(
                    and_(
                        # CaseManager.cmt == cmt.name,
                        # CaseManager.state == cmt.state,
                        # CaseManager.facilities == cmt.facility_name
                        Patient.case_manager_id == case_manager.cm_id
                    )).count()
                print(f"Patient count for Case Manager {case_manager.id}: {patient_count}")
                total_patient_count += patient_count
                            # Get performance metrics
            performance = db.session.query(
                func.count(distinct(CaseManager.id)).label('total_case_managers'),
                func.sum(CaseManagerPerformance.tx_cur).label('total_tx_cur'),
                func.sum(CaseManagerPerformance.iit).label('total_iit'),
                func.sum(CaseManagerPerformance.transferred_out).label('transferred_out'),
                func.sum(CaseManagerPerformance.dead).label('total_dead'),
                func.sum(CaseManagerPerformance.discontinued).label('total_discontinued'),
                func.sum(CaseManagerPerformance.appointments_completed).label('total_appointments_completed'),
                func.sum(CaseManagerPerformance.appointments_schedule).label('total_appointments_scheduled'),
                func.sum(CaseManagerPerformance.viral_load_suppressed).label('total_vl_suppressed'),
                func.sum(CaseManagerPerformance.viral_load_samples).label('total_vl_samples'),
                func.sum(CaseManagerPerformance.viral_load_results).label('total_vl_results'),
                func.sum(CaseManagerPerformance.viral_load_eligible).label('total_vl_eligible'),
                func.avg(CaseManagerPerformance.final_score).label('average_score')
            ).select_from(CaseManagerPerformance).join(
                CaseManager,
                and_(
                    CaseManager.id == CaseManagerPerformance.CaseManagerID,
                    CaseManager.cmt == cmt.name,
                    CaseManager.state == cmt.state,
                    CaseManager.facilities == cmt.facility_name
                )
            ).first()

            # Create the response data
            cmt_data = cmt_schema.dump(cmt)
            cmt_data['case_managers'] = [
                {
                    'id': cm.id,
                    'fullname': cm.fullname,
                    'role': cm.role,
                    'state': cm.state,
                    'facilities': cm.facilities,
                    'created_at': cm.created_at.isoformat() if cm.created_at else None
                }
                for cm in case_managers
            ]
            cmt_data['patient_count'] = total_patient_count

            # Add performance metrics if available
            if performance:
                total_appointments = performance.total_appointments_scheduled or 1
                total_results = performance.total_vl_results or 1

                cmt_data['performance'] = {
                    'case_managers_count': performance.total_case_managers,
                    'tx_cur': performance.total_tx_cur or 0,
                    'iit': performance.total_iit or 0,
                    'transferred_out': performance.transferred_out or 0,
                    'dead': performance.total_dead or 0,
                    'discontinued': performance.total_discontinued or 0,
                    'appointments': {
                        'completed': performance.total_appointments_completed or 0,
                        'scheduled': performance.total_appointments_scheduled or 0,
                        'completion_rate': ((performance.total_appointments_completed or 0) / total_appointments) * 100
                    },
                    'viral_load': {
                        'suppressed': performance.total_vl_suppressed or 0,
                        'eligible': performance.total_vl_eligible or 0,
                        'samples': performance.total_vl_samples or 0,
                        'results': performance.total_vl_results or 0,
                        'suppression_rate': ((performance.total_vl_suppressed or 0) / total_results) * 100
                    },
                    'average_score': round(performance.average_score or 0, 2)
                }

            return cmt_data

        except Exception as e:
            db.session.rollback()
            raise e
