from dotenv import load_dotenv
load_dotenv()  

from app import create_app, db
# No need to create another Migrate instance

app = create_app()
# Remove the redundant: migrate = Migrate(app, db)

# Add this block to explicitly import all models
# from app.models import user, patient, case_manager, cmt, facility, appointments, performance

if __name__ == '__main__':
    app.run(debug=True)