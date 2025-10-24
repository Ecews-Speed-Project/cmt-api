from calendar import week
from operator import or_
import re
from app.models import DrugPickup, ViralLoad, CaseManager, CMT, Patient, Facility, CaseManagerPerformance, State
from app import db
from sqlalchemy import func, and_, or_, case, literal, literal_column, text, cast, Date, Integer, Float
from datetime import datetime, timedelta
import logging
from .performance_service import PerformanceService

logger = logging.getLogger(__name__)

class DashboardService:
    @staticmethod
    def _get_date_range_from_next_appointment():
        """Get min and max dates from DrugPickup.next_appointment_date field"""
        date_range = db.session.query(
            func.min(DrugPickup.next_appointment_date).label('min_date'),
            func.max(DrugPickup.next_appointment_date).label('max_date')
        ).first()
        
        return date_range.min_date, date_range.max_date

    @staticmethod
    def get_stats(start_date, end_date, user):
        try:
            #logger.info(f"Getting stats for user {str(user.user_id)} from {start_date} to {end_date}")
            
            # Get date range from next_appointment_date field if not provided
            if not start_date or not end_date:
                start_date, end_date = DashboardService._get_date_range_from_next_appointment()
                logger.info(f"Using date range from next_appointment_date: {start_date} to {end_date}")

            # Get base query for patients based on user role
            patient_query = Patient.query
            if 'Super Admin' not in user['roles']:
                if 'State' in user['roles']:
                    patient_query = patient_query.join(State, State.id == user['state_id']).filter(Patient.state == State.name)
                elif 'Admin' in user['roles']:
                    patient_query = patient_query.join(State, State.id == user['state_id']).filter(Patient.state == State.name)

            vl_query = ViralLoad.query
            if 'Super Admin' not in user['roles']:
                if 'State' in user['roles']:
                    vl_query = vl_query.join(State, State.id == user['state_id']).filter(ViralLoad.state == State.name)
                elif 'Admin' in user['roles']:
                    vl_query = vl_query.join(State, State.id == user['state_id']).filter(ViralLoad.state == State.name)
            
            # Convert dates for SQL Server compatibility
            current_date = func.cast(func.getdate(), Date)
            art_start = cast(Patient.art_start_date, Date)

            # TX_CUR: Active patients
            tx_cur = patient_query.filter(
                Patient.current_art_status == "Active"
            ).count()

            
            total_days_to_add = cast(cast(Patient.days_of_arv_refill, Float), Integer) + 28
            iit_date = func.dateadd(
                text('day'),
                total_days_to_add,
                Patient.pharmacy_last_pickup_date
            )

            # IIT: Inactive patients
            iit = patient_query.filter(
                Patient.current_art_status != "Active",
                Patient.outcomes == "",
                iit_date.between(start_date, end_date)
            ).count()

            # Drug Pickup Appointments
            drug_pickup = patient_query.filter(
                Patient.pharmacy_last_pickup_date.between(start_date, end_date),
                Patient.pharmacy_last_pickup_date != None
                ).count()

            # Viral Load Stats with corrected query
            vl_eligible = patient_query.filter(
                Patient.current_art_status == 'Active',
                cast(Patient.days_on_art, Integer) >= 180,
                ).count()
            
            vl_eligible2 = vl_query.count()
            
            # Viral Load Results
           
            vl_results = patient_query.filter(
                Patient.current_art_status == 'Active',
                cast(Patient.days_on_art, Integer) >= 180,
                    # Handle NULL or empty string cases properly
                and_(
                        Patient.current_viral_load != None,  
                        # Patient.current_viral_load != ''
                    ),
                    # Fix date comparison
                func.datediff(
                        text('day'),
                        Patient.date_of_current_viral_load,
                        literal(end_date)
                    ) >= 0,
                func.datediff(
                        text('day'),
                        Patient.date_of_current_viral_load,
                        literal(end_date)
                    ) <= 365
            ).count()

            # Viral Load Suppressed
            vl_suppressed = patient_query.filter(
                Patient.current_art_status == 'Active',
                cast(Patient.days_on_art, Integer) >= 180,
                    # Handle NULL or empty string cases properly
                and_(
                        Patient.current_viral_load != None,  
                        # Patient.current_viral_load != ''
                    ),
                    # Fix date comparison
                func.datediff(
                        text('day'),
                        Patient.date_of_current_viral_load,
                        literal(end_date)
                    ) >= 0,
                func.datediff(
                        text('day'),
                        Patient.date_of_current_viral_load,
                        literal(end_date)
                    ) <= 365,
                Patient.current_viral_load < 1000.0
                ).count()
            vl_collected = patient_query.filter(
                Patient.current_art_status == 'Active',
                func.datediff(
                            text('day'),
                            art_start,
                            current_date
                        ) >= 180,
                    # Handle NULL or empty string cases properly
                
                Patient.last_date_of_sample_collection.between(start_date, end_date)
            ).count()
            return {
                'tx_cur': tx_cur,
                'iit': iit,
                'drug_pickup': drug_pickup,
                'viral_load': {
                    'eligible': vl_eligible or 0,
                    'eligible2': vl_eligible2 or 0,
                    'total_results': vl_results or 0,
                    'suppressed': vl_suppressed or 0,
                    'collected': vl_collected or 0
                },
            }
        except Exception as e:
            logger.error(f"Error getting stats: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def get_trends(start_date, end_date, user):
        # Get date range from next_appointment_date field if not provided
        if not start_date or not end_date:
            start_date, end_date = DashboardService._get_date_range_from_next_appointment()
            logger.info(f"Using trend date range from next_appointment_date: {start_date} to {end_date}")

        appointments = DashboardService._get_appointment_trends(start_date, end_date, user)
        viral_loads = DashboardService._get_viral_load_trends(start_date, end_date, user)
        total_visits = DashboardService._get_visit_trends(start_date, end_date, user)
        
        return {
            'drug_pickups': appointments, 
            'viral_loads': viral_loads,
            'total_visit': total_visits
        }

    @staticmethod
    def _get_appointment_trends(start_date, end_date, user):
        # Calculate the number of weeks between start and end dates
        total_days = (end_date - start_date).days
        num_weeks = (total_days // 7) + (1 if total_days % 7 > 0 else 0)
        
        # Generate weekly periods
        week_periods = []
        for i in range(num_weeks):
            week_start = start_date + timedelta(days=i*7)
            week_end = week_start + timedelta(days=6)  # End of week (inclusive)
            week_label = f"Week{i+1}"
            
            if week_end > end_date:
                week_end = end_date
                
            week_periods.append((week_start, week_end, week_label))
        
        appt_results = []
        
        # For each week period, calculate appointment counts
        for week_start, week_end, week_label in week_periods:
            # Use next_appointment_date field directly
            expected_appointment = DrugPickup.next_appointment_date
            
            # Count patients with expected appointments within this week who showed up
            query = db.session.query(
                func.count(DrugPickup.id.distinct()).label('count')
            ).join(
                Patient,
                and_(
                    Patient.pep_id == DrugPickup.pep_id,
                    Patient.datim_code == DrugPickup.datim_code,
                    # Check that patient has a newer pickup date (indicating they showed up)
                    Patient.pharmacy_last_pickup_date > DrugPickup.pharmacy_last_pickup_date,
                    # Filter by date range from your SQL query
                    Patient.pharmacy_last_pickup_date.between(week_start, week_end),
                )
            ).filter(
                # Only include appointments with expected dates in this week
                expected_appointment.between(week_start, week_end)
            )
            
            # Apply user role-based filtering
            if 'Super Admin' not in user['roles']:
                if 'State' in user['roles']:
                    query = query.join(State, State.id == user['state_id']).filter(Patient.state == State.name)
                elif 'Admin' in user['roles']:
                    query = query.join(State, State.id == user['state_id']).filter(Patient.state == State.name)
            
            count = query.scalar() or 0  # Get count or default to 0
            appt_results.append({
                'week_label': week_label,
                'week_start': week_start.strftime('%Y-%m-%d'),
                'week_end': week_end.strftime('%Y-%m-%d'),
                'count': count
            })
        
        return appt_results
    
    @staticmethod
    def _get_viral_load_trends(start_date, end_date, user):
        # Calculate the number of weeks between start and end dates
        total_days = (end_date - start_date).days
        num_weeks = (total_days // 7) + (1 if total_days % 7 > 0 else 0)
        
        # Generate weekly periods
        week_periods = []
        for i in range(num_weeks):
            week_start = start_date + timedelta(days=i*7)
            week_end = week_start + timedelta(days=6)  # End of week (inclusive)
            week_label = f"Week{i+1}"
            
            if week_end > end_date:
                week_end = end_date
                
            week_periods.append((week_start, week_end, week_label))
        
        vl_results = []
        
        # For each week period, calculate appointment counts
        for week_start, week_end, week_label in week_periods:
            # Use next_appointment_date field directly
            expected_appointment = DrugPickup.next_appointment_date
            
            # Count patients with expected appointments within this week who showed up
            query = db.session.query(
                func.count(ViralLoad.id.distinct()).label('count')
            ).join(
                Patient,
                and_(
                    Patient.pep_id == ViralLoad.pep_id,
                    Patient.datim_code == ViralLoad.datim_code,
                    # Check that patient has a newer pickup date (indicating they showed up)
                    Patient.last_date_of_sample_collection > ViralLoad.last_date_of_sample_collection,
                    # Filter by date range from your SQL query
                    Patient.last_date_of_sample_collection.between(week_start, week_end),
                )
            ).filter(
                # Only include appointments with expected dates in this week
                expected_appointment.between(week_start, week_end)
            )

            
            
            # Apply user role-based filtering
            if 'Super Admin' not in user['roles']:
                if 'State' in user['roles']:
                    query = query.join(State, State.id == user['state_id']).filter(Patient.state == State.name)
                elif 'Admin' in user['roles']:
                    query = query.join(State, State.id == user['state_id']).filter(Patient.state == State.name)

            count = query.scalar() or 0  # Get count or default to 0
            vl_results.append({
                'week_label': week_label,
                'week_start': week_start.strftime('%Y-%m-%d'),
                'week_end': week_end.strftime('%Y-%m-%d'),
                'count': count
            })
        
        return vl_results

    @staticmethod
    def _get_visit_trends(start_date, end_date, user):
        # Calculate the number of weeks between start and end dates
        total_days = (end_date - start_date).days
        num_weeks = (total_days // 7) + (1 if total_days % 7 > 0 else 0)
        
        # Generate weekly periods
        week_periods = []
        for i in range(num_weeks):
            week_start = start_date + timedelta(days=i*7)
            week_end = week_start + timedelta(days=6)  # End of week (inclusive)
            week_label = f"Week{i+1}"
            
            if week_end > end_date:
                week_end = end_date
                
            week_periods.append((week_start, week_end, week_label))
        
        visit_results = []
        
        # For each week period, calculate appointment counts
        for week_start, week_end, week_label in week_periods:
                        
            # Count patients with expected appointments within this week who showed up
            query = db.session.query(
                func.count(Patient.id.distinct()).label('count')
            ).filter(
                # Only include appointments with expected dates in this week
                Patient.pharmacy_last_pickup_date.between(week_start, week_end)
            )
            
            # Apply user role-based filtering
            if 'Super Admin' not in user['roles']:
                if 'State' in user['roles']:
                    query = query.join(State, State.id == user['state_id']).filter(Patient.state == State.name)
                elif 'Admin' in user['roles']:
                    query = query.join(State, State.id == user['state_id']).filter(Patient.state == State.name)

            count = query.scalar() or 0  # Get count or default to 0
            visit_results.append({
                'week_label': week_label,
                'week_start': week_start.strftime('%Y-%m-%d'),
                'week_end': week_end.strftime('%Y-%m-%d'),
                'count': count
            })
        
        return visit_results
    
    @staticmethod
    def get_top_case_managers(user):
        """
        Get top 3 unique case managers based on their highest final score.
        Uses window functions for better performance.
        Args:
            user: The current user with role and access information
        Returns:
            List[dict]: Top 3 unique case managers with their performance data
        """
        try:
            logger.info(f"Getting top case managers for user {str(user['user_id'])}")
            
            # Use ROW_NUMBER window function to rank case managers by their highest score
            ranked_subquery = db.session.query(
                CaseManagerPerformance,
                CaseManager,
                func.row_number().over(
                    partition_by=CaseManagerPerformance.CaseManagerID,
                    order_by=CaseManagerPerformance.final_score.desc()
                ).label('rn')
            ).join(
                CaseManager,
                CaseManagerPerformance.CaseManagerID == CaseManager.id
            )
            
            # Apply state filter if needed
            if 'Super Admin' not in user['roles']:
                if 'Admin' in user['roles'] or 'State' in user['roles']:
                    ranked_subquery = ranked_subquery.join(
                        State,
                        State.name == CaseManager.state
                    ).filter(State.id == user['state_id'])
            
            ranked_subquery = ranked_subquery.subquery()
            
            # Get only the top score for each case manager (rn = 1) and limit to top 3
            query = db.session.query(
                ranked_subquery
            ).filter(
                ranked_subquery.c.rn == 1
            ).order_by(
                ranked_subquery.c.final_score.desc()
            ).limit(3)

            results = query.all()
            logger.info(f"Retrieved {len(results)} top unique case managers")
            
            # Debug logging
            if len(results) < 3:
                logger.warning(f"Expected 3 unique case managers but got {len(results)}")

            top_case_managers = []
            for row in results:
                top_case_managers.append({
                    'case_manager_id': row.id,
                    'fullname': row.fullname,
                    'role': row.role,
                    'cmt': row.cmt,
                    'facility': row.facilities,
                    'State': row.state,
                    'final_score': row.final_score,
                })

            return top_case_managers

        except Exception as e:
            logger.error(f"Error getting top case managers: {str(e)}", exc_info=True)
            return []
    
    @staticmethod
    def get_top_cmts(user):
        """
        Get top 3 CMTs based on their aggregated final scores.
        Args:
            user: The current user with role and access information
        Returns:
            List[dict]: Top 3 CMTs with their performance data
        """
        try:
            logger.info(f"Getting top CMTs for user {str(user['user_id'])}")
            
            # Use a subquery to get the highest score for each unique case manager
            # This ensures we don't double-count case managers who have multiple roles
            unique_cm_subquery = db.session.query(
                CaseManager.cmt,
                CaseManager.state,
                CaseManager.facilities,
                CaseManagerPerformance.CaseManagerID,
                func.max(CaseManagerPerformance.final_score).label('max_score')
            ).join(
                CaseManagerPerformance,
                CaseManager.id == CaseManagerPerformance.CaseManagerID
            ).group_by(
                CaseManager.cmt,
                CaseManager.state,
                CaseManager.facilities,
                CaseManagerPerformance.CaseManagerID
            ).subquery()
            
            # Main query to aggregate scores by CMT
            query = db.session.query(
                unique_cm_subquery.c.cmt.label('cmt'),
                unique_cm_subquery.c.state.label('state'),
                unique_cm_subquery.c.facilities.label('facility'),
                func.avg(unique_cm_subquery.c.max_score).label('final_score')
            ).group_by(
                unique_cm_subquery.c.cmt,
                unique_cm_subquery.c.state,
                unique_cm_subquery.c.facilities
            )
            
            # Apply user filters based on role
            if 'Super Admin' not in user['roles']:
                if 'Admin' in user['roles'] or 'State' in user['roles']:
                    # Join with State table to filter by state_id
                    query = query.join(
                        State,
                        State.name == unique_cm_subquery.c.state
                    ).filter(State.id == user['state_id'])
            
            # Order by final score and limit to top 3
            query = query.order_by(
                func.avg(unique_cm_subquery.c.max_score).desc()
            ).limit(3)
            
            results = query.all()
            logger.info(f"Retrieved {len(results)} top CMTs")
            
            # Debug logging
            if len(results) < 3:
                logger.warning(f"Expected 3 CMTs but got {len(results)}")
            
            top_cmts = []
            for row in results:
                top_cmts.append({
                    'cmt': row.cmt,
                    'state': row.state,
                    'facility': row.facility if hasattr(row, 'facility') else None,
                    'final_score': float(row.final_score) if row.final_score else 0.0
                })
            
            return top_cmts
            
        except Exception as e:
            logger.error(f"Error getting top CMTs: {str(e)}", exc_info=True)
            return []
