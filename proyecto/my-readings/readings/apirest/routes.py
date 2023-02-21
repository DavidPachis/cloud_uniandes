from apirest import api
from apirest.views import RecursoArchivo, RecursoMiTask, RecursoRegistro, RecursoLogin, RecursoLibro, RecursoLibros, RecursoMiLibro, RecursoTasks
#, RecursoTarjeta, RecursoTarjetas

api.add_resource(RecursoRegistro, '/api/auth/signup')
api.add_resource(RecursoLogin, '/api/auth/login')
api.add_resource(RecursoTasks, '/api/tasks')
api.add_resource(RecursoMiTask, '/api/tasks/<int:id_task>')
api.add_resource(RecursoArchivo, '/api/tasks/<filename>')

# /api/reviews?limit=num_post&order=desc|asc
# api.add_resource(RecursoLibros, '/api/reviews')

api.add_resource(RecursoLibros, '/api/libros')
api.add_resource(RecursoMiLibro, '/api/libros/<string:id_libro>')
