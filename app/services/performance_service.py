from app.models import CaseManagerPerformance, CaseManager, State, CMT, Patient
from app import db
from sqlalchemy import func, and_, or_, distinct
from sqlalchemy.inspection import inspect
from datetime import datetime
import logging


logger = logging.getLogger(__name__)

class PerformanceService:
    @staticmethod
    def _apply_pediatrics_filter(query, pediatrics_filter: bool = False):
        """
        Apply pediatrics/adolescents filter (0–19 years or age in months > 0)
        """
        if pediatrics_filter:
            query = query.filter(
                or_(
                    and_(
                        Patient.current_age >= 0,
                        Patient.current_age <= 19
                    ),
                    Patient.current_age_months > 0
                )
            )
        return query

    @staticmethod
    def _apply_pmtct_filter(query, pmtct_filter: bool = False):
        """
        Apply PMTCT filter: female patients who are pregnant or breastfeeding.
        """
        if pmtct_filter:
            query = query.filter(
                and_(
                    func.lower(Patient.sex) == 'f',
                    func.lower(Patient.current_pregnancy_status).in_(
                        ['pregnant', 'breastfeeding']
                    )
                )
            )
        return query

    @staticmethod
    def get_case_managers_performance(user, pediatrics_filter: bool = False, pmtct_filter: bool = False):
        """
        Get All case managers based on their final score.
        Args:
            user: The current user with role and access information
        Returns:
            List[dict]:  case managers with their performance data
        """
        try:
            logger.info(f"Getting case managers for user {str(user['user_id'])}")
            
            query = db.session.query(CaseManagerPerformance, CaseManager).join(
                CaseManager,
                CaseManagerPerformance.CaseManagerID == CaseManager.id
            )

            # Apply user filters based on role
            if 'Super Admin' not in user['roles']:
                if 'Admin' in user['roles'] or 'State' in user['roles']:
                    query = query.join(
                        State,
                        State.name == CaseManager.state
                    ).filter(State.id == user['state_id'])

            # Apply cohort filters based on patients (used only to decide which CMs to include)
            if pediatrics_filter or pmtct_filter:
                query = query.join(
                    Patient,
                    Patient.case_manager_id == CaseManager.cm_id
                )
                query = PerformanceService._apply_pediatrics_filter(query, pediatrics_filter)
                query = PerformanceService._apply_pmtct_filter(query, pmtct_filter)
                query = query.distinct()

            results = query.all()
            logger.info(f"Retrieved {len(results)} case managers")

            case_managers = []
            for perf, cm in results:
                performance_data = {
                    column.name: getattr(perf, column.name)
                    for column in CaseManagerPerformance.__table__.columns
                }
                case_manager_data = {
                    column.name: getattr(cm, column.name)
                    for column in CaseManager.__table__.columns
                }
                case_managers.append({
                    'performance': performance_data,
                    'case_manager': case_manager_data
                })

            return case_managers

        except Exception as e:
            logger.error(f"Error getting case managers: {str(e)}", exc_info=True)
            return []

    @staticmethod
    def get_cmt_performance(user, pediatrics_filter: bool = False, pmtct_filter: bool = False):
        """Get aggregated performance data by CMT.
        Cohort filters (pediatrics / PMTCT) are used only to decide which CMTs to include,
        not to recompute cohort-restricted metrics.
        """
        try:
            logger.info(f"Getting CMT performance for user {str(user['user_id'])}")
            # Query to get performance data grouped by CMT
            query = db.session.query(
                CMT.name.label('cmt'),
                CMT.state,
                CMT.facility_name,
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
                func.sum(CaseManagerPerformance.fy_viral_load_eligible).label('total_fy_vl_eligible'),
                func.sum(CaseManagerPerformance.viral_load_eligible).label('total_vl_eligible'),
                func.avg(CaseManagerPerformance.final_score).label('average_score')
            ).join(
                CaseManager,
                and_(
                    CaseManager.cmt == CMT.name,
                    CaseManager.state == CMT.state,
                    CaseManager.facilities == CMT.facility_name
                )
            ).join(
                CaseManagerPerformance,
                CaseManager.id == CaseManagerPerformance.CaseManagerID
            )

            # Apply cohort filters based on patients (used only to decide which CMTs to include)
            if pediatrics_filter or pmtct_filter:
                query = query.join(
                    Patient,
                    Patient.case_manager_id == CaseManager.cm_id
                )
                query = PerformanceService._apply_pediatrics_filter(query, pediatrics_filter)
                query = PerformanceService._apply_pmtct_filter(query, pmtct_filter)

            query = query.group_by(
                CMT.name,
                CMT.state,
                CMT.facility_name
            )

            # Apply user role filters
            if 'Super Admin' not in user['roles']:
                if 'Admin' in user['roles'] or 'State' in user['roles']:
                    query = query.join(
                        State,
                        State.name == CaseManager.state
                    ).filter(State.id == user['state_id'])

            results = query.all()
            logger.info(f"Retrieved performance data for {len(results)} CMTs")

            cmt_performance = []
            for result in results:
                total_appointments = result.total_appointments_scheduled or 1  # Avoid division by zero
                total_results = result.total_vl_results or 1  # Avoid division by zero
                
                cmt_performance.append({
                    'cmt': result.cmt,
                    'state': result.state,
                    'facility_name': result.facility_name,
                    'case_managers_count': result.total_case_managers,
                    'tx_cur': result.total_tx_cur or 0,
                    'iit': result.total_iit or 0,
                    'transferred_out': result.transferred_out or 0,
                    'dead': result.total_dead or 0,
                    'discontinued': result.total_discontinued or 0,
                    'appointments': {
                        'completed': result.total_appointments_completed or 0,
                        'scheduled': result.total_appointments_scheduled or 0,
                        'completion_rate': ((result.total_appointments_completed or 0) / total_appointments) * 100
                    },
                    'viral_load': {
                        'suppressed': result.total_vl_suppressed or 0,
                        'fy_eligible': result.total_fy_vl_eligible or 0,
                        'eligible': result.total_vl_eligible or 0,
                        'samples': result.total_vl_samples or 0,
                        'results': result.total_vl_results or 0,
                        'suppression_rate': ((result.total_vl_suppressed or 0) / total_results) * 100
                    },
                    'average_score': round(result.average_score or 0, 2)
                })

            return cmt_performance

        except Exception as e:
            logger.error(f"Error getting CMT performance: {str(e)}", exc_info=True)
            return []

    @staticmethod
    def get_single_case_manager_performance(case_manager_id, user):
        """Get all performance data records for a single case manager"""
        try:
            logger.info(f"Getting performance for case manager {case_manager_id}")
            
            query = db.session.query(CaseManagerPerformance, CaseManager).join(
                CaseManager,
                CaseManagerPerformance.CaseManagerID == CaseManager.id
            ).filter(CaseManager.id == case_manager_id)

            # Apply user role filters
            if 'Super Admin' not in user['roles']:
                if 'Admin' in user['roles'] or 'State' in user['roles']:
                    query = query.join(
                        State,
                        State.name == CaseManager.state
                    ).filter(State.id == user['state_id'])

            results = query.all()
            if not results:
                return None

            # Get the first performance record and case manager (all results are for the same case manager)
            perf, cm = results[0]
            
            # Get patients for this case manager - explicitly select all columns
            patients = db.session.query(Patient).filter(
                Patient.case_manager_id == cm.cm_id
            ).all()
            
            # Manually serialize patients - use __dict__ to get all loaded attributes
            patients_data = []
            for patient in patients:
                patient_data = {}
                # Get all attributes from the patient instance
                # This includes all loaded column values
                for key, value in patient.__dict__.items():
                    # Skip SQLAlchemy internal attributes
                    if key.startswith('_'):
                        continue
                    
                    # Handle datetime objects - convert to ISO format string
                    if isinstance(value, datetime):
                        patient_data[key] = value.isoformat() if value else None
                    else:
                        patient_data[key] = value
                patients_data.append(patient_data)

            performance_data = {
                column.name: getattr(perf, column.name)
                for column in CaseManagerPerformance.__table__.columns
            }
            
            case_manager_data = {
                column.name: getattr(cm, column.name)
                for column in CaseManager.__table__.columns
            }

            logger.info(f"Found performance data for case manager {case_manager_id} with {len(patients_data)} patients")
            
            return {
                'performance': performance_data,
                'case_manager': case_manager_data,
                'patients': patients_data
            }

        except Exception as e:
            logger.error(f"Error getting case manager performance: {str(e)}", exc_info=True)
            return None

    @staticmethod
    def get_single_cmt_performance(cmt_name, user):
        """Get performance data for a single CMT"""
        try:
            logger.info(f"Getting performance for CMT {cmt_name}")
            
            query = db.session.query(
                CaseManager.cmt,
                CaseManager.state,
                
                func.count(CaseManager.id).label('total_case_managers'),
                func.sum(CaseManagerPerformance.tx_cur).label('total_tx_cur'),
                func.sum(CaseManagerPerformance.iit).label('total_iit'),
                func.sum(CaseManagerPerformance.transferred_out).label('transferred_out'),
                func.sum(CaseManagerPerformance.dead).label('total_dead'),
                func.sum(CaseManagerPerformance.discontinued).label('total_discontinued'),
                func.sum(CaseManagerPerformance.appointments_completed).label('total_appointments_completed'),
                func.sum(CaseManagerPerformance.appointments_schedule).label('total_appointments_scheduled'),
                func.sum(CaseManagerPerformance.viral_load_suppressed).label('total_vl_suppressed'),
                func.sum(CaseManagerPerformance.viral_load_results).label('total_vl_results'),
                func.sum(CaseManagerPerformance.fy_viral_load_eligible).label('total_fy_vl_eligible'),
                func.sum(CaseManagerPerformance.viral_load_eligible).label('total_vl_eligible'),
                func.avg(CaseManagerPerformance.final_score).label('average_score')
            ).join(
                CaseManagerPerformance,
                CaseManager.id == CaseManagerPerformance.CaseManagerID
            ).filter(
                CaseManager.cmt == cmt_name
            ).group_by(
                CaseManager.cmt,
                CaseManager.state
            )

            if 'Super Admin' not in user['roles']:
                if 'Admin' in user['roles'] or 'State' in user['roles']:
                    query = query.join(
                        State,
                        State.name == CaseManager.state
                    ).filter(State.id == user['state_id'])

            result = query.first()
            if not result:
                return None

            total_appointments = result.total_appointments_scheduled or 1
            total_results = result.total_vl_results or 1

            return {
                'cmt': result.cmt,
                'state': result.state,
                'case_managers_count': result.total_case_managers,
                'tx_cur': result.total_tx_cur or 0,
                'iit': result.total_iit or 0,
                'transferred_out': result.transferred_out or 0,
                'dead': result.total_dead or 0,
                'discontinued': result.total_discontinued or 0,
                'appointments': {
                    'completed': result.total_appointments_completed or 0,
                    'scheduled': result.total_appointments_scheduled or 0,
                    'completion_rate': ((result.total_appointments_completed or 0) / total_appointments) * 100
                },
                'viral_load': {
                    'suppressed': result.total_vl_suppressed or 0,
                    'fy_eligible': result.total_fy_vl_eligible or 0,
                    'eligible': result.total_vl_eligible or 0,
                    'results': result.total_vl_results or 0,
                    'suppression_rate': ((result.total_vl_suppressed or 0) / total_results) * 100
                },
                'average_score': round(result.average_score or 0, 2)
            }

        except Exception as e:
            logger.error(f"Error getting CMT performance: {str(e)}", exc_info=True)
            return None