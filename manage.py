from flask_migrate import Migrate

from app import app, db

migrate = Migrate(app, db)

with app.app_context():
    db.drop_all()
    db.create_all()
