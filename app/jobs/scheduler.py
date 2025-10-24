from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import os
from app.utils.db_utils import execute_sql_file

class FlaskScheduler:
    def __init__(self):
        self.app = None
        self.scheduler = BackgroundScheduler()
        self.scripts_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'utils', 'scripts'
        )

    def run_daily_performance_query(self):
        """Run the daily case manager performance query"""
        with self.app.app_context():
            sql_path = os.path.join(
                self.scripts_dir,
                'Case_Manager_Performance_Query_v1.3.sql'
            )
            execute_sql_file(sql_path)

    def run_monthly_performance_query(self):
        """Run the monthly case manager performance query"""
        with self.app.app_context():
            sql_path = os.path.join(
                self.scripts_dir,
                'Case_Manager_All_Performance_Query_v1.3.sql'
            )
            execute_sql_file(sql_path)

    def init_scheduler(self, app):
        """Initialize the scheduler with jobs"""
        self.app = app
        
        # Daily performance job at midnight
        self.scheduler.add_job(
            self.run_daily_performance_query,
            # trigger=CronTrigger(minute='*/2'),
            trigger=CronTrigger(hour=0, minute=0, second=0),
            id='daily_performance_calculation',
            name='Daily Case Manager Performance',
            replace_existing=True
        )

        # Monthly performance job at midnight on last day
        self.scheduler.add_job(
            self.run_monthly_performance_query,
            trigger=CronTrigger(
                day='last',  # Run on last day of month
                hour=0,
                minute=0,
                second=0
            ),
            id='monthly_performance_calculation',
            name='Monthly Case Manager Performance',
            replace_existing=True
        )
        
        self.scheduler.start()
        return self.scheduler

# Create singleton instance
flask_scheduler = FlaskScheduler()
