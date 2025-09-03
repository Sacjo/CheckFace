from flask import Flask
from flask_cors import CORS
from routes.recognition_routes import recognition_routes
from routes.attendance_routes import attendance_routes
from routes.student_routes    import student_routes

app = Flask(__name__)

# Habilita CORS para permitir solicitudes desde React (localhost:3000)
CORS(app)

# Registra las rutas
app.register_blueprint(recognition_routes)
app.register_blueprint(attendance_routes)
app.register_blueprint(student_routes)

if __name__ == "__main__":
    app.run(debug=True)
