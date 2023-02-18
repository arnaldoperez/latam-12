from flask_sqlalchemy import SQLAlchemy
from firebase_admin import storage
import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__="user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(300), unique=False, nullable=False)
    picture = db.Column(db.String(50), unique=False, nullable=True)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)
    is_admin = db.Column(db.Boolean(), unique=False, nullable=False)
    profile_picture_id=db.Column(db.Integer, db.ForeignKey("imagen.id"))
    profile_picture=db.relationship("Imagen")

    def __repr__(self):
        return f'<User {self.email}>'

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }

class TokenBlockedList(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    token= db.Column(db.String(1000), unique=True, nullable=False)
    email = db.Column(db.String(200), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "token": self.token,
            "email": self.email,
            "created_at": self.created_at
        }

class Product(db.Model):
    __tablename__="product"
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(250))
    price=db.Column(db.Float)
    picture_id=db.Column(db.Integer, db.ForeignKey("imagen.id"))
    picture=db.relationship("Imagen")

class Imagen(db.Model):
    __tablename__="imagen"
    id=db.Column(db.Integer, primary_key=True)
    resource_path=db.Column(db.String(250),unique=True, nullable=False)
    description=db.Column(db.String(200))

    def serialize(self):
        return {
            "id": self.id,
            "resource_path": self.resource_path,
            "description": self.description,
        }

    def image_url(self):
        bucket=storage.bucket(name="clase-imagenes-flask.appspot.com")
        resource=bucket.blob(self.resource_path)
        signed_url=resource.generate_signed_url(version="v4", expiration=datetime.timedelta(minutes=15), method="GET")
        return {
            "id": self.id,
            "resource_path": self.resource_path,
            "signed_url": signed_url
        }