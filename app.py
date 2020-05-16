from flask import Flask, jsonify, request
from CustomObjects import CustomObject1
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float
import os
from flask_marshmallow import Marshmallow

# app registration
app = Flask(__name__)

# db registration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'dbname.db')

db = SQLAlchemy(app)
ma = Marshmallow(app) # needed for flask_marshmallow

# db creation
@app.cli.command('db_create') # wywolanie w konsoli : flask db_create
def db_create():
    db.create_all()
    print('Db created')

# db destroying
@app.cli.command('db_drop') # wywolanie w konsoli : flask db_drop
def db_drop():
    db.drop_all()
    print('db dropped')

# seeding db
@app.cli.command('db_seed') # wywolanie w konsoli : flask db_seed
def db_seed():
    mercury = Planet(planet_name='Mercury',
                    planet_type='Class D',
                    home_star='Sol',
                    mass=3.258e23,
                    radius=1516,
                    distance=35.98e6)
    venus = Planet(planet_name='Venus',
                    planet_type='Class K',
                    home_star='Sol',
                    mass=4.867e24,
                    radius=3760,
                    distance=67.24e6)
    earth = Planet(planet_name='Earth',
                    planet_type='Class M',
                    home_star='Sol',
                    mass=5.972e24,
                    radius=3959,
                    distance=92.96e6)
    db.session.add(mercury)
    db.session.add(venus)
    db.session.add(earth)

    test_user = User(first_name='William', last_name='Herschel', email='test@test.com', password='P@ssw0rd')
    db.session.add(test_user)
    db.session.commit()
    print('db seeded')
    

# API ENDPOINTS
@app.route("/", methods=['GET'])
def home():
    return jsonify(message='Hello')


@app.route("/super_simple", methods=['GET'])
def super_simple():
    return jsonify(message = "Hello from the Planetary API")


@app.route("/custom_object/<string:name>/<int:age>/", methods=['GET'])
def custom_object(name: str, age: int):
    obj = CustomObject1(nazwa=name, wiek=age)
    return jsonify(message='utworzono obiekt z parametrami', objName=obj.nazwa, objAge=obj.wiek), 200 # 200 nie trzeba,, jak u gory bez zadnego to by default 200


@app.route("/not_working_test", methods=['GET']) # just to simulate the 404 status code
def not_working_test():
    return jsonify(message='not found'), 404


@app.route('/planets', methods=['GET'])
def planets():
    planets_list = Planet.query.all()
    deserialized_list_of_planets = planets_schema.dump(planets_list)
    return jsonify(deserialized_list_of_planets), 200



# DB MODELS
class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)


class Planet(db.Model):
    __tablename__ = 'planets'
    planet_id = Column(Integer, primary_key=True)
    planet_name = Column(String)
    planet_type = Column(String)
    home_star = Column(String)
    mass = Column(Float)
    radius = Column(Float)
    distance = Column(Float)

class UserSchema(ma.Schema): # needed for flask_marshmallow so that it can serialize User class to json
    class Meta:
        fields = ('id', 'first_name', 'last_name', 'email', 'password')

class PlanetSchema(ma.Schema): # needed for flask_marshmallow so that it can serialize Planet class to json
    class Meta:
        fields = ('planet_id', 'planet_name', 'planet_type', 'home_star', 'mass', 'radius', 'distance')

user_schema = UserSchema() # will be used to get single record
users_schema = UserSchema(many=True) # will be used to get the list of records

planet_schema = PlanetSchema() # same as above
planets_schema = PlanetSchema(many=True) # same as above
    


# run app statement
if __name__ == '__main__':
    app.run()