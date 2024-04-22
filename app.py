from datetime import datetime
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://user:password@localhost/mydatabase"
# "postgresql://user:password@localhost/mydatabase"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
Migrate(app, db)
api = Api(app)


"""
Definicion de los modelos de la base de datos
"""
class Usuario(db.Model):
    __tablename__ = 'Usuario'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(64), nullable=False)
    apellidos = db.Column(db.String(128), nullable=False, unique=True)
    rut = db.Column(db.String(9), nullable=False)
    fecha_nacimiento = db.Column(db.Date, nullable=False) 
    cargo = db.Column(db.String(128), nullable=False)
    edad = db.Column(db.Integer, nullable=False)
    proyectos = db.relationship('Proyecto', backref='Usuario', lazy=True)

    def __init__(self, nombre, apellidos, rut, fecha_nacimiento, cargo):
        self.nombre = nombre
        self.apellidos = apellidos
        self.rut = rut
        self.fecha_nacimiento = fecha_nacimiento
        self.cargo = cargo
        self.edad = self.set_edad()

    def __repr__(self):
        return '<Usuario %r>' % self.nombre
    
    def set_edad(self):
        today = datetime.today()
        tmp_nacimiento = datetime.strptime(self.fecha_nacimiento, "%Y-%m-%d")
        self.edad = today.year - tmp_nacimiento.year - (
            (today.month, today.day) < (tmp_nacimiento.month, tmp_nacimiento.day)
            )
        return self.edad
    
    @property
    def serialize(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'apellidos': self.apellidos,
            'rut': self.rut,
            'fecha_nacimiento': self.fecha_nacimiento.isoformat(),
            'cargo': self.cargo,
            'edad': self.edad,
        }
    

class Proyecto(db.Model):
    __tablename__ = 'Proyecto'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(64), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('Usuario.id'))
    institucion_id = db.Column(db.Integer, 
                                        db.ForeignKey('Institucion.id'))
    usuario = db.relationship('Usuario', backref='Proyecto', lazy=True)
    institucion = db.relationship('Institucion', backref='Proyecto', lazy=True)
    
    def __init__(self, nombre, descripcion, fecha_inicio, fecha_fin,
                 institucion_id, usuario_id):
        self.nombre = nombre
        self.descripcion = descripcion
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.institucion_id = institucion_id
        self.usuario_id = usuario_id

    def __repr__(self):
        return '<Proyecto %r>' % self.nombre
    
    @property
    def serialize(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'fecha_inicio': self.fecha_inicio.isoformat(),
            'fecha_fin': self.fecha_fin.isoformat(),
            'institucion': self.institucion_id,
            'usuario_id': self.usuario_id,
        }
    

class Institucion(db.Model):
    __tablename__ = 'Institucion'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(64), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    direccion = db.Column(db.String(128), nullable=False)
    fecha_creacion = db.Column(db.DateTime(timezone=True), 
                               server_default=func.now()) 
    proyecto = db.relationship('Proyecto', backref='Institucion', lazy=True)


    def __init__(self, nombre, descripcion, direccion):
        self.nombre = nombre
        self.descripcion = descripcion
        self.direccion = direccion

    def __repr__(self):
        return '<Institucion %r>' % self.nombre

    @property
    def serialize(self):
        
        return {
            "id": self.id,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "direccion": self.direccion,
            "fecha_creacion": self.fecha_creacion.isoformat(),
        }


""" 
    CRUD para Instituciones con get, post, put y delete
    Ademas su correspondiente listar todas las instituciones
"""
class InstitucionesResource(Resource):
    def get(self):
        return [institucion.serialize for institucion in Institucion.query.all()]
    
    def post(self):
        data = request.get_json()
        institucion = Institucion(
                                    nombre=data['nombre'],  
                                    descripcion=data['descripcion'],
                                    direccion=data['direccion'],
                                )
        db.session.add(institucion)
        db.session.commit()
        return institucion.serialize


class InstitucionResource(Resource):
    def get(self, pk):
        try:
            tmp = Institucion.query.filter_by(id=pk).first()
            return tmp.serialize
        except:
            return {"Mensaje": "No existe la institucion con id {}".format(pk)}
    
    def put(self, pk):
        try:
            data = request.get_json()
            institucion = Institucion.query.filter_by(id=pk).first()
            institucion.nombre = data['nombre']
            institucion.descripcion = data['descripcion']
            institucion.direccion = data['direccion']
            db.session.commit()
            return institucion.serialize
        except:
            return {"Mensaje": "No existe la institucion con id {}".format(pk)}

    def delete(self, pk):
        instance_institucion = Institucion.query.filter_by(id=pk).first()
        tmp_nombre = instance_institucion.nombre
        db.session.delete(instance_institucion)
        db.session.commit()
        mensaje = "Se ha eliminado la institucion con nombre {} con lleva el id {}".format(tmp_nombre, pk)
        return {"Mensaje": mensaje}


"""
    Servicios para listar Proyectos y Usuarios con post para cada uno
"""
class ProyectosResource(Resource):
    def get(self):
        return [proyecto.serialize for proyecto in Proyecto.query.all()]

    def post(self):
        data = request.get_json()
        proyecto = Proyecto(
                                nombre=data['nombre'],
                                descripcion=data['descripcion'],
                                fecha_inicio=data['fecha_inicio'],
                                fecha_fin=data['fecha_fin'],
                                institucion_id=data['institucion_id'],
                                usuario_id=data['usuario_id'],
                            )
        db.session.add(proyecto)
        db.session.commit()
        return proyecto.serialize


class UsuariosResource(Resource):
    def get(self):
        return [usuario.serialize for usuario in Usuario.query.all()]

    def post(self):
        data = request.get_json()
        usuario = Usuario(
                            nombre=data['nombre'],
                            apellidos=data['apellidos'],
                            rut=data['rut'],
                            fecha_nacimiento=data['fecha_nacimiento'],
                            cargo=data['cargo'],
                        )
        db.session.add(usuario)
        db.session.commit()
        return usuario.serialize


"""
Servicio por filtro
"""
class Servicio1Resource(Resource):
    """
    Crear servicio para listar una institución (Filtró por id) con sus
    respectivos proyectos y responsable del proyecto
    """
    def get(self, pk):
        query1 = Proyecto.query.filter_by(institucion_id=pk).all()
        query2 = Institucion.query.filter_by(id=pk).first()
        serializer_data = []
        
        institucion_data = {
            "id": query2.id,
            "nombre": query2.nombre,
            "descripcion": query2.descripcion,
            "direccion": query2.direccion,
            "fecha_creacion": query2.fecha_creacion.isoformat(),
        }
        tmp_proyectos = []
        for obj in query1:
            proyectos_data = {
                "id": obj.id,
                "nombre": obj.nombre,
                "descripcion": obj.descripcion,
                "fecha_inicio": obj.fecha_inicio.isoformat(),
                "fecha_fin": obj.fecha_fin.isoformat(),
                "usuario": {
                        "id": obj.usuario.id,
                        "nombre": obj.usuario.nombre,
                        "apellidos": obj.usuario.apellidos,
                        "rut": obj.usuario.rut,
                        "fecha_nacimiento": obj.usuario.fecha_nacimiento.isoformat(),
                        "cargo": obj.usuario.cargo,
                        "edad": obj.usuario.edad, 
                }
            }
            tmp_proyectos.append(proyectos_data)
        institucion_data["proyectos"] = tmp_proyectos
        serializer_data.append(institucion_data)
        return jsonify(serializer_data)


class Servicio2Resource(Resource):
    """
    Crear servicio para listar un usuario (filtro por Rut) con sus respectivos
    proyectos.
    """
    def get(self, rut):
        query1 = Usuario.query.filter_by(rut=rut).first()
        query2 = Proyecto.query.filter_by(usuario_id=query1.id).all()
        usuario_data = {
            "id": query1.id,
            "nombre": query1.nombre,
            "apellidos": query1.apellidos,
            "rut": query1.rut,
            "fecha_nacimiento": query1.fecha_nacimiento.isoformat(),
            "cargo": query1.cargo,
            "edad": query1.edad,
        }
        serializer_data = []
        tmp_proyectos = []
        for obj in query2:
            proyecto_data = {
                "id": obj.id,
                "nombre": obj.nombre,
                "descripcion": obj.descripcion,
                "fecha_inicio": obj.fecha_inicio.isoformat(),
                "fecha_fin": obj.fecha_fin.isoformat(),
                "institucion": obj.institucion.nombre,
            }
            tmp_proyectos.append(proyecto_data)
        usuario_data["proyectos"] = tmp_proyectos
        serializer_data.append(usuario_data)

        return jsonify(serializer_data)


class Servicio4Resource(Resource):
    """
    Crear servicio para listar los proyectos que la respuesta sea el nombre
    del proyecto y los días que faltan para su término.
    """
    def get(self):
        query1 = Proyecto.query.all()
        fecha = datetime.now()
        tmp_proyectos = []
        serializer_data = []
        for obj in query1:
            if obj.fecha_fin > fecha.date():
                proyecto_data = {}
                dias_faltantes = obj.fecha_fin - fecha.date()
                proyecto_data["nombre"] = obj.nombre
                proyecto_data["dias_faltantes"] = dias_faltantes.days
                tmp_proyectos.append(proyecto_data)
        serializer_data.append(tmp_proyectos)
        return jsonify(serializer_data)
    

api.add_resource(InstitucionResource, '/institucion/<int:pk>')
api.add_resource(InstitucionesResource, '/instituciones')
api.add_resource(ProyectosResource, '/proyectos')
api.add_resource(UsuariosResource, '/usuarios')
api.add_resource(Servicio1Resource, '/servicio1/<int:pk>')
api.add_resource(Servicio2Resource, '/servicio2/<string:rut>')
api.add_resource(Servicio4Resource, '/servicio4')


if __name__ == '__main__':
    app.run(debug=True)
