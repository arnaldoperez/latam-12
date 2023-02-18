"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for, send_from_directory
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from api.utils import APIException, generate_sitemap
from api.models import db, TokenBlockedList
from api.routes import api
from api.admin import setup_admin
from api.commands import setup_commands
from firebase_admin import auth
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from api.app_routes.users import apiUser

import firebase_admin
from firebase_admin import credentials

credentials_file=os.path.abspath(os.curdir) + "/firebase-credentials.json"
print(credentials_file)
cred = credentials.Certificate(credentials_file)
firebase_admin.initialize_app(cred)

#from models import Person

ENV = os.getenv("FLASK_ENV")
static_file_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../public/')
app = Flask(__name__)
print(__name__)
app.url_map.strict_slashes = False

# Configuracion de JWT
app.config["JWT_SECRET_KEY"] = os.getenv("FLASK_APP_KEY")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 60
jwt = JWTManager(app)

@jwt.token_in_blocklist_loader
def check_token_blocklist(jwt_header, jwt_payload)-> bool:
    if jwt_payload['role']=="password" and request.path!="/api/resetpassword":
        return True
    if jwt_payload["type"]=="refresh":
        token_is_blocked=TokenBlockedList.query.filter_by(token=jwt_payload['access_jti']).first()
        if token_is_blocked is not None:
            return True

    TokenBlocked = TokenBlockedList.query.filter_by(token=jwt_payload['jti']).first()
    if isinstance(TokenBlocked, TokenBlockedList):
        return True
    else:
        return False

@jwt.token_verification_loader
def custom_verify_token(jwt_header, jwt_payload)-> bool:
    print("Verificacion")
    try:
        token=request.Authorization.split(" ")[1]
        print(token)
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        if uid is None:
            return False
        return True
    except:
        print("error")
        return False


# Configuracion de BCrypt

# database condiguration
db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db, compare_type = True)
db.init_app(app)

# Allow CORS requests to this API
CORS(app)

# add the admin
setup_admin(app)

# add the admin
setup_commands(app)

# Add all endpoints form the API with a "api" prefix
app.register_blueprint(api, url_prefix='/api')
#app.register_blueprint(apiUser, url_prefix='/user')

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    #print(app.url_map)
    if ENV == "development":
        return generate_sitemap(app)
    return send_from_directory(static_file_dir, 'index.html')

# any other endpoint will try to serve it like a static file
@app.route('/<path:path>', methods=['GET'])
def serve_any_other_file(path):
    if not os.path.isfile(os.path.join(static_file_dir, path)):
        path = 'index.html'
    response = send_from_directory(static_file_dir, path)
    response.cache_control.max_age = 0 # avoid cache memory
    return response

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3001))
    app.run(host='0.0.0.0', port=PORT, debug=True)
