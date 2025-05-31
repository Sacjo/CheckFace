import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    # Base directory: .../app/webapp
    base_dir = os.path.abspath(os.path.dirname(__file__))

    # Carpeta de archivos estáticos y plantillas
    static_folder   = os.path.join(base_dir, 'static')
    template_folder = os.path.join(base_dir, 'templates')

    app = Flask(
        __name__,
        static_folder=static_folder,
        static_url_path='/static',
        template_folder=template_folder
    )

    app.config.update({
        'SQLALCHEMY_DATABASE_URI': 'postgresql+pg8000://postgres:root@localhost:5432/checkface',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SECRET_KEY': os.environ.get('SECRET_KEY', 'root'),
    })

    db.init_app(app)
    with app.app_context():
        db.create_all()

    from .routes import main
    app.register_blueprint(main)

    return app
