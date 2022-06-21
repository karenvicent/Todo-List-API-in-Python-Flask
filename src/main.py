"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Todolist
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response ",
        "sucess": "True"
    }

    return jsonify(response_body), 200

@app.route('/todolist', methods=['GET'])
def get_todas_las_tareas():
    alltareas = Todolist.query.all()
    tareas = list(map(lambda n: n.serialize(),alltareas))
    return jsonify(tareas), 200

@app.route('/todolist', methods=['POST'])
def add_tarea():
    body = request.get_json()
    tarea = Todolist(text=body['text'], done=body['done'])
    db.session.add(tarea)
    db.session.commit()

    respuesta = {
        "msg": "Tarea creada exitosamente"
    }
    return jsonify(respuesta), 200

@app.route('/todolistdelete/<int:id>/', methods=['DELETE'])
def delete_tarea(id):
    tarea = Todolist.query.get(id)
    if tarea is None:
        raise APIException("Tarea no encontrada", status_code=404)
    db.session.delete(tarea)
    db.session.commit()
        
    respuesta = {
        "msg": "Tarea borrada exitosamente"
    }
    return jsonify(respuesta), 200


# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
