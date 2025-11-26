from datetime import datetime, timedelta
from sqlalchemy import and_, func, cast, Date, text

from app import db
from app.models import Patient, DrugPickup, ViralLoad, CaseManager


class CaseManagerMobileService:
    @staticmethod
    def get_stats(case_manager_id: str) -> dict:
        """Return key stats for a specific case manager.

        Metrics returned:
        - total_patients, tx_cur, iit, dead, transferred_out, stopped
        - viral_load: eligible, total_results, suppressed, collected
        - appointments: total, upcoming, past_due
        """
        cm = CaseManager.query.filter_by(id=case_manager_id).first()
        if not cm:
            return {
                'total_patients': 0,
                'tx_cur': 0,
                'iit': 0,
                'dead': 0,
                'transferred_out': 0,
                'stopped': 0,
                'viral_load': {
                    'eligible': 0,
                    'total_results': 0,
                    'suppressed': 0,
                    'collected': 0,
                },
                'appointments': {
                    'total': 0,
                    'upcoming': 0,
                    'past_due': 0,
                },
            }
        cm_id = cm.cm_id
        # Base filters
        patient_base = Patient.query.filter(Patient.case_manager_id == cm_id)

        # Totals by status/outcomes
        total_patients = patient_base.count()
        tx_cur = patient_base.filter(Patient.current_art_status == "Active").count()

        # IIT approximation similar to dashboard logic when no explicit range is provided
        total_days_to_add = cast(cast(Patient.days_of_arv_refill, db.Integer), db.Integer) + 28
        iit_date = func.dateadd(text('day'), total_days_to_add, Patient.pharmacy_last_pickup_date)
        iit = patient_base.filter(
            Patient.current_art_status != "Active",
            (Patient.outcomes == None) | (Patient.outcomes == ""),
        ).count()

        dead = patient_base.filter(Patient.outcomes == "Dead").count()
        transferred_out = patient_base.filter(Patient.outcomes == "Transferred out").count()
        stopped = patient_base.filter(Patient.outcomes == "Stopped").count()

        # Viral load metrics (last 12 months window for results/collections)
        vl_base = ViralLoad.query.filter(ViralLoad.case_manager == case_manager_id)
        today = func.cast(func.getdate(), Date)
        twelve_months_ago = func.dateadd(text('day'), -365, today)

        vl_eligible = vl_base.count()

        vl_results = patient_base.filter(
            Patient.current_art_status == 'Active',
            cast(Patient.days_on_art, db.Integer) >= 180,
            Patient.current_viral_load != None,
            and_(Patient.date_of_current_viral_load >= twelve_months_ago,
                 Patient.date_of_current_viral_load <= today),
        ).count()

        vl_suppressed = patient_base.filter(
            Patient.current_art_status == 'Active',
            cast(Patient.days_on_art, db.Integer) >= 180,
            Patient.current_viral_load != None,
            and_(Patient.date_of_current_viral_load >= twelve_months_ago,
                 Patient.date_of_current_viral_load <= today),
            Patient.current_viral_load < 1000.0,
        ).count()

        # Patients whose sample collection date is greater than the VL model's recorded sample collection date
        vl_collected = db.session.query(func.count(func.distinct(Patient.id))).join(
            ViralLoad,
            and_(
                Patient.pep_id == ViralLoad.pep_id,
                Patient.datim_code == ViralLoad.datim_code,
            )
        ).filter(
            Patient.case_manager_id == cm_id,
            Patient.last_date_of_sample_collection != None,
            ViralLoad.last_date_of_sample_collection != None,
            Patient.last_date_of_sample_collection > ViralLoad.last_date_of_sample_collection,
        ).scalar() or 0

        # Appointment stats from DrugPickup for this CM
        appt_base = db.session.query(DrugPickup).filter(DrugPickup.case_manager == case_manager_id)
        appt_total = appt_base.count()
        appt_upcoming = appt_base.filter(DrugPickup.next_appointment_date != None,
                                         DrugPickup.next_appointment_date >= func.getdate()).count()
        appt_past_due = appt_base.filter(DrugPickup.next_appointment_date != None,
                                         DrugPickup.next_appointment_date < func.getdate()).count()

        return {
            'total_patients': total_patients or 0,
            'tx_cur': tx_cur or 0,
            'iit': iit or 0,
            'dead': dead or 0,
            'transferred_out': transferred_out or 0,
            'stopped': stopped or 0,
            'viral_load': {
                'eligible': vl_eligible or 0,
                'total_results': vl_results or 0,
                'suppressed': vl_suppressed or 0,
                'collected': vl_collected or 0,
            },
            'appointments': {
                'total': appt_total or 0,
                'upcoming': appt_upcoming or 0,
                'past_due': appt_past_due or 0,
            },
        }


