from datetime import date, time, datetime, timezone, timedelta
from api.models import db, User, TokenBlockedList, Imagen
from flask_jwt_extended import create_access_token, create_refresh_token,get_jti, jwt_required, get_jwt_identity, get_jwt
from api.utils import generate_sitemap, APIException
from flask_bcrypt import Bcrypt
from flask import Flask, Blueprint, request, jsonify
from firebase_admin import storage
from ..sendmail import mailtemplate_password_recovery, send_mail
import tempfile


app=Flask(__name__)
bcrypt=Bcrypt(app)

apiUser = Blueprint('apiUser', __name__)

@apiUser.route("/hellouser",methods=["GET"])
def helloUser():    
    return "Hello User", 200

@apiUser.route('/login', methods=['POST'])
def login():
    email = request.json.get("email", None)
    password = request.json.get("password", None)

    user = User.query.filter_by(email=email).first()
    
    # Verificamos el nombre de usuario
    if user is None:
        return jsonify({"message":"Login failed"}), 401
    
    # Validar clave    
    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({"message":"Wrong password"}), 401
    
    if(user.is_admin):
        claims={"role":"admin"}
    else:
        claims={"role":"client"}

    access_token = create_access_token(identity=user.id, additional_claims=claims)
    claims["access_jti"]=get_jti(access_token)
    refresh_token=create_refresh_token(identity=user.id, additional_claims=claims)
    return jsonify({"accessToken":access_token, "refreshToken":refresh_token})

@apiUser.route('/signup', methods=['POST'])
def signup():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    try:
        password=bcrypt.generate_password_hash(password,10).decode("utf-8")
        user = User(email=email, password=password, is_active=True, is_admin=False)
        db.session.add(user)
        db.session.commit()
        return jsonify({"message":"Usuario registrado"}), 201
    except Exception as err:
        db.session.rollback()
        print(err)
        return jsonify({"message":"internal error"}), 500

@apiUser.route('/refresh',methods=['POST'])
@jwt_required(refresh=True)
def refreshToken():
    claims=get_jwt()
    refreshToken = claims["jti"]
    accessToken = claims["access_jti"]
    id=get_jwt_identity()
    now = datetime.now(timezone.utc)
    accessTokenBlocked = TokenBlockedList(token=accessToken, created_at=now, email=get_jwt_identity())
    refreshTokenBlocked = TokenBlockedList(token=refreshToken, created_at=now, email=get_jwt_identity())
    db.session.add(accessTokenBlocked)
    db.session.add(refreshTokenBlocked)
    db.session.commit()
    claims={"role":claims['role']}
    access_token = create_access_token(identity=id,additional_claims=claims)
    claims["access_jti"]=get_jti(access_token)
    refresh_token=create_refresh_token(identity=id, additional_claims=claims)
    return jsonify({"accessToken":access_token, "refreshToken":refresh_token})

@apiUser.route('/uploadPhoto', methods=['POST'])
@jwt_required()
def uploadPhoto():
    user_id=get_jwt_identity()
    user = User.query.get(user_id)
    if user is None:
        return "Usuario no encontrado", 403

    # Se recibe un archivo en la peticion
    file=request.files['profilePic']
    # Extraemos la extension del archivo
    extension=file.filename.split(".")[1]
    # Guardar el archivo recibido en un archivo temporal
    temp = tempfile.NamedTemporaryFile(delete=False)
    file.save(temp.name)
    # Subir el archivo a firebase
    ## Se llama al bucket
    bucket=storage.bucket(name="clase-imagenes-flask.appspot.com")
    # Se genera el nombre de archivo con el id de la imagen y la extension
    filename="profiles/" + str(user_id) + "." + extension
    ## Se hace referencia al espacio dentro del bucket
    resource = bucket.blob(filename)
    ## Se sube el archivo temporal al espacio designado en el bucket
    # Se debe especificar el tipo de contenido en base a la extension
    resource.upload_from_filename(temp.name,content_type="image/"+extension)
    
    # Guardar imagen en base de datos si no existe previamente
    if Imagen.query.filter(Imagen.resource_path==filename).first() is None:
        new_image=Imagen(resource_path=filename, description="Profile photo of user "+ str(user_id))
        db.session.add(new_image)
        # Procesar las operaciones de la base de datos, pero sin cerrarla para poder 
        # ejecutar mas operaciones posteriormente
        db.session.flush()
        #Buscamos el usuario en la BD partiendo del id del token
        # Actualizar el campo de la foto
        user.profile_picture_id=new_image.id
        # Se crear el registro en la base de datos 
        db.session.add(user)
        db.session.commit()
    
    return "Ok", 200


@apiUser.route('/helloprotected', methods=['GET'])
@jwt_required()
def handle_hello_protected():
    claims=get_jwt()
    user = User.query.get(get_jwt_identity())
    response_body = {
        "message": "token válido",
        "user_id": get_jwt_identity(),
        "role":claims["role"],
        "user_email": user.email
    }

    return jsonify(response_body), 200


@apiUser.route('/getPhoto', methods=['GET'])
@jwt_required()
def getPhoto():
    #Buscamos el usuario en la BD partiendo del id del token
    user = User.query.get(get_jwt_identity())
    if user is None:
        return "Usuario no encontrado", 403
   
    url=user.profile_picture.image_url()
        
    return jsonify({"pictureUrl":url}), 200


@apiUser.route('/logout', methods=['POST'])
@jwt_required()
def destroyToken():
    jwt = get_jwt()["jti"]
    now = datetime.now(timezone.utc)
    tokenBlocked = TokenBlockedList(token=jwt, created_at=now, email=get_jwt_identity())
    db.session.add(tokenBlocked)
    db.session.commit()

    return jsonify(msg="Acceso revocado")

@apiUser.route('/resetpassword', methods=['POST'])
@jwt_required()
def reset_password():
    claims=get_jwt()
    if claims['role']=="password":
        id_user=get_jwt_identity()
        user=User.query.get(id_user)
        request_password=request.json.get('password')
        password=bcrypt.generate_password_hash(request_password,10).decode("utf-8")
        user.password=password
        db.session.add(user)
        db.session.flush()
        now = datetime.now(timezone.utc)
        tokenBlocked = TokenBlockedList(token=claims['jti'], created_at=now, email=get_jwt_identity())
        db.session.add(tokenBlocked)
        db.session.commit()
        return jsonify({"msg":"Clave cambiada"}), 200
    else:
        return jsonify({"msg":"Cambio de clave no permitido"}), 401
    
@apiUser.route('/requestresetpassword', methods=['POST'])
def request_password_reset():
    email=request.json.get('email')
    user=User.query.filter(User.email==email).first()
    if user is None:
        return jsonify({"msg":"Enlace de reinicio de contraseña enviado al correo"})

    claims={"role":"password"}
    delta=timedelta(minutes=5)
    password_token=create_access_token(identity=user.id,additional_claims=claims, expires_delta=delta)
    # ToDo: Envio de enlace por correo aqui
    template=mailtemplate_password_recovery(password_token)
    if send_mail(email, template):
        return jsonify({"msg":"Enlace de reinicio de contraseña enviado al correo"})
    else:
        return jsonify({"msg":"Error en reinicio de contraseña"})
