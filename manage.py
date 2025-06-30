from flask_migrate import Migrate
from dotenv import load_dotenv
from app import create_app, db

load_dotenv()

app = create_app()
migrate = Migrate(app, db)

if __name__ == '__main__':
    app.run()
