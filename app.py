from flask import Flask
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)


class Prueba(Resource):
    def get(self):
        return {
            "una": "lol",
            "dos": "lel"
        }


api.add_resource(Prueba, '/')

if __name__ == '__main__':
    app.run(debug=True)
