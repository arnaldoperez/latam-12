"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from flask import Flask, request, jsonify, url_for, Blueprint
from api.models import db, User, TokenBlockedList
from api.utils import generate_sitemap, APIException
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from flask_bcrypt import Bcrypt
from datetime import date, time, datetime, timezone
from .sendmail import send_mail
from flask_jwt_extended import JWTManager


from api.app_routes import apiUser, apiProduct

api = Blueprint('api', __name__)

app=Flask(__name__)
bcrypt=Bcrypt(app)

api.register_blueprint(apiUser)
api.register_blueprint(apiProduct)

@api.route('/hello', methods=['POST', 'GET'])
def handle_hello():
    response_body = {
        "message": "Hello! I'm a message that came from the backend, check the network tab on the google inspector and you will see the GET request"
    }
    #send_mail()
    return jsonify(response_body), 200

#print(app.url_map)