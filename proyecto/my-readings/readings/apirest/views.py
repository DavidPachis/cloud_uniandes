from datetime import datetime, timedelta
import os
from os import getcwd
from flask import request, current_app, send_from_directory
from werkzeug.utils import secure_filename
from flask_restful import Resource, reqparse
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, JWTManager
from flask_restful import Api

from apirest import api, db
from apirest.models import Task, TaskSchema, Usuario, task_schema, tasks_schema #, Libro,  libro_schema, libros_schema


PATH_FILE = getcwd() + "/my-readings/readings/archivos/"
PATH_FILE_COMPRESS = getcwd() + "/my-readings/readings/archivosComprimidos/"

def crear_carpeta(usuario):
    try:
        file = PATH_FILE+usuario
        fileCompress = PATH_FILE_COMPRESS+usuario
        print(file)
        os.makedirs(file)
        os.makedirs(fileCompress)
    except print(0):
        pass
'''
Recurso que administra el servicio de login
'''
class RecursoLogin(Resource):
    def post(self):
        request.get_json(force=True)
        usuario = Usuario.query.get(request.json['usuario'])
        
        if usuario is None:
            return {'message':'El email ingresado no está registrado'}, 400
        
        if not usuario.verificar_clave(request.json['password']):
            return {'message': 'Contraseña incorrecta'}, 400
        
        try:
            access_token = create_access_token(identity = request.json['usuario'], expires_delta = timedelta(days = 1))
            return {
                'message':'Sesion iniciada',
                'access_token':access_token
            }
        
        except:
            return {'message':'Ha ocurrido un error'}, 500
    
'''
Recurso que administra el servicio de registro
'''
class RecursoRegistro(Resource):
    def post(self):
        if Usuario.query.filter_by(email=request.json['email']).first() is not None:
            return {'message': f'El correo({request.json["email"]}) ya está registrado'}, 400
        
        if request.json['email'] == '' or request.json['password'] == '' or request.json['password1'] == '' or request.json['usuario'] == '':
            return {'message': 'Campos invalidos'}, 400
        
        if request.json['password'] != request.json['password1']:
            return {'message': 'contraseña no coincide'}, 400
        
        nuevo_usuario = Usuario(
            email = request.json['email'],
            password = request.json['password'],
            usuario = request.json['usuario'],
        )
        
        nuevo_usuario.hashear_clave()

        try:
            db.session.add(nuevo_usuario)
            db.session.commit()
            access_token = create_access_token(identity = request.json['email'], expires_delta = timedelta(days = 1))
            crear_carpeta(nuevo_usuario.usuario)
            return {
                'message': f'El correo {request.json["email"]} ha sido registrado',
                'access_token': access_token 
            }

        except:
            return {'message':'Ha ocurrido un error'}, 500

'''
Recurso que lista todas los libros de los usuarios
'''
class RecursoLibro(Resource):
    def get(self):        
        parser = reqparse.RequestParser()
        parser.add_argument('limit', type = int, help='El limite no puede ser convertido')
        parser.add_argument('order')
        args = parser.parse_args()
        
        if args['order'] == 'desc':
            libros = Libro.query.order_by(db.desc(Libro.id)).limit(args['limit']).all()
        else:
            libros = Libro.query.order_by(db.asc(Libro.id)).limit(args['limit']).all()
        
        return libros_schema.dump(libros)    

'''
Recurso que administra el servicio de todas los de un usuario
'''
class RecursoLibros(Resource):
    @jwt_required()
    def get(self):        
        email = get_jwt_identity()        
        libros = Libro.query.filter_by(usuario_libro = email).order_by(db.desc(Libro.id)).all()
        return libros_schema.dump(libros)    
    
    @jwt_required()
    def post(self):
        email = get_jwt_identity()
        
        nueva_libro = Libro(
            titulo = request.json['titulo'],
            autor = request.json['autor'],
            categoria = request.json['categoria'],
            descripcion = request.json['descripcion'],
            idioma = request.json['idioma'],
            fecha_publicacion = request.json['fecha_publicacion'],
            revision = request.json['revision'],          
            usuario_libro = email
            )

        db.session.add(nueva_libro)
        db.session.commit()
        
        return libro_schema.dump(nueva_libro)
    
class RecursoTasks(Resource):
    @jwt_required()
    def get(self):        
        usuario = get_jwt_identity() 
        args = request.args
        order = args.get('order')
        max = args.get('max')      
        if int(order) == 0:
            tasks = Task.query.filter_by(usuario_task = usuario).order_by(db.asc(Task.id_task)).limit(int(max)).all()
        if int(order) == 1:
            tasks = Task.query.filter_by(usuario_task = usuario).order_by(db.desc(Task.id_task)).limit(int(max)).all()
        return tasks_schema.dump(tasks)   
    
    @jwt_required()
    def post(self):
        usuario = get_jwt_identity()

        if Task.query.filter_by(filename=request.json['filename']).first() is not None:
            return {'message': f'El filename({request.json["filename"]}) ya está registrado'}, 400
        
        new_task = Task(
            filename = request.json['filename'],
            rutaArchivo = PATH_FILE,
            rutaCompresion = PATH_FILE_COMPRESS,
            status = "uploaded",
            tipoConversion = request.json['tipoConversion'],
            fechaCarga = datetime.now(),         
            usuario_task = usuario
            )
        
        db.session.add(new_task)
        db.session.commit()
        
        return task_schema.dump(new_task)

'''
Recurso que administra el servicio de una publicación (Detail)
'''

class RecursoMiTask(Resource):
    @jwt_required()
    def get(self, id_task):
        usuario = get_jwt_identity()
        task = Task.query.get(id_task)

        if task is None:
            return {'message':'La tarea no está registrada'}, 400
        else:
            return task_schema.dump(task)
        
    @jwt_required()
    def put(self, id_task):
        email = get_jwt_identity()
        task = Task.query.get_or_404(id_task)        
        
        if Task.usuario_task != email:
            return {'message':'No tiene acceso a esta tarea'}, 401

        if 'filename' in request.json:
            Task.filename = request.json['filename']
        
        if 'status' in request.json:
            Task.status = request.json['status']

        if 'tipoConversion' in request.json:
            Task.tipoConversion = request.json['tipoConversion']

        db.session.commit()
        return TaskSchema.dump(task)

    @jwt_required()
    def delete(self, id_task):
        usuario = get_jwt_identity()
        task = Task.query.get(id_task)
        
        if task is None:
            return {'message':'La tarea no está registrada'}, 400
        else:
            db.session.delete(task)
            db.session.commit()        
            return 'El resgistro ha sido eliminado'
    
class RecursoArchivo(Resource):
    @jwt_required()
    def get(self, filename):
        email = get_jwt_identity()
        name = Task.query.filter_by(filename = filename)
        archivoOriginal = "./my-readings/readings/Archivos/"+name
        archivoProcesado = "./my-readings/readings/ArchivosComprimidos/"+name

        if Task.usuario_task != email:
            return {'message':'No tiene acceso a esta tarea'}, 401
        else:
            return TaskSchema.dump()
    
class RecursoMiLibro(Resource):
    @jwt_required()
    def get(self, id_libro):
        email = get_jwt_identity()
        libro = Libro.query.get_or_404(id_libro)

        if libro.usuario_libro != email:
            return {'message':'No tiene acceso a esta publicación'}, 401
        else:
            return libro_schema.dump(libro)

    @jwt_required()
    def put(self, id_libro):
        email = get_jwt_identity()
        libro = Libro.query.get_or_404(id_libro)        
        
        if libro.usuario_libro != email:
            return {'message':'No tiene acceso a este concurso'}, 401

        if 'titulo' in request.json:
            libro.titulo = request.json['titulo']
        
        if 'autor' in request.json:
            libro.autor = request.json['autor']

        if 'categoria' in request.json:
            libro.categoria = request.json['categoria']

        if 'descripcion' in request.json:
            libro.descripcion = request.json['descripcion']

        if 'idioma' in request.json:
            libro.idioma = request.json['idioma']

        if 'descripcion' in request.json:
            libro.descripcion = request.json['descripcion']

        if 'fecha_publicacion' in request.json:
            libro.fecha_publicacion = request.json['fecha_publicacion']

        if 'revision' in request.json:
            libro.revision = request.json['revision']

        db.session.commit()
        return libro_schema.dump(libro)

    @jwt_required()
    def delete(self, id_libro):
        email = get_jwt_identity()
        libro = Libro.query.get_or_404(id_libro)
        
        if libro.usuario_libro != email:
            return {'message':'No tiene acceso a esta publicación'}, 401
        
        db.session.delete(libro)
        db.session.commit()        
        return '', 204
        