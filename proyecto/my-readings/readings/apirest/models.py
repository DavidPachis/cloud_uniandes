import enum
from werkzeug.security import generate_password_hash, check_password_hash
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from apirest import ma, db

class IdiomaCategoria(str, enum.Enum):
    EN = "Inglés"
    ES = "Español"
    JP = "Japones"
    
class Categoria(str, enum.Enum):
    COL = "Literatura Colombiana"
    UNI = "Literatura Universal"
    COMIC = "Literatura Gráfica y Cómic"
    LATAM = "Literatura Latinoamericana"
    FANTASIA = "Fantasía"
    FICCION = "Ficción"

'''
Modelos
'''
class Usuario(db.Model):
    usuario = db.Column(db.String(100), primary_key = True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    tasks = db.relationship('Task', backref = 'usuario', lazy = True)

    def hashear_clave(self):
        '''
        Hashea la clave en la base de datos
        '''
        self.password = generate_password_hash(self.password, 'sha256')

    def verificar_clave(self, clave):
        '''
        Verifica la clave hasheada con la del parámetro
        '''
        return check_password_hash(self.password, clave)
    

class Task(db.Model):
    id_task = db.Column(db.Integer, primary_key = True, autoincrement=True)
    filename = db.Column(db.String(1000))
    rutaArchivo = db.Column(db.String(1000))
    rutaCompresion = db.Column(db.String(1000))
    status = db.Column(db.String(50))
    tipoConversion = db.Column(db.String(10))
    fechaCarga = db.Column(db.DateTime())
    usuario_task = db.Column(db.String(100), db.ForeignKey('usuario.usuario'), nullable = False)


'''
class Libro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100))
    autor = db.Column(db.String(100))
    categoria = db.Column(db.Enum(Categoria))
    idioma = db.Column(db.Enum(IdiomaCategoria))
    descripcion = db.Column(db.String(280))
    fecha_publicacion = db.Column(db.DateTime(), default = datetime.now)
    revision = db.Column(db.String(280))
    #usuario_libro = db.Column(db.String(100), db.ForeignKey('usuario.email'), nullable = False)
'''
'''
Schemas
'''
class UsuarioSchema(ma.Schema):
    '''
    Representa el schema de un admin
    '''
    class Meta:
        fields = ("usuario", "email", "password")

class TaskSchema(ma.Schema):
    '''
    Representa el schema de un concurso
    '''
    class Meta:
        fields = ("id", "nombre", "rutaArchivo", "rutaCompresion", "disponible", "tipoConversion", "fechaCarga", "usuario_task")

usuario_schema = UsuarioSchema()
task_schema = TaskSchema()
tasks_schema = TaskSchema(many = True)
