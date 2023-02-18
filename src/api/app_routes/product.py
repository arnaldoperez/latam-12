from datetime import date, time, datetime, timezone
from api.models import db, User, TokenBlockedList, Product
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from api.utils import generate_sitemap, APIException
from flask import Blueprint, request, jsonify
#from ..routes import bcrypt

apiProduct = Blueprint('apiProduct', __name__)

@apiProduct.route('/product', methods=['POST'])
@jwt_required()
def create_product():
    role=get_jwt()["role"]
    isAdmin=role=="admin"
    if(isAdmin): # Si es admin, hace la insersion
        name = request.json.get("name", None)
        price = request.json.get("price", None)
        product=Product(name=name,price=price)
        db.session.add(product)
        db.session.commit()
        return jsonify({"msj":"Producto creado con exito"}), 201
    else: # Si no es admin, no tiene acceso al recurso
        return jsonify({"msj":"No tiene acceso a este recurso"}), 403


@apiProduct.route('/product', methods=['GET'])
def get_product():
    return jsonify({"message":"internal error"}), 500
