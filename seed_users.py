from app.webapp import create_app, db
from app.webapp.models import User

app = create_app()
with app.app_context():
    root = User(username='root')
    root.set_password('root')
    db.session.add(root)
    db.session.commit()
    print("Usuario root creado.")
