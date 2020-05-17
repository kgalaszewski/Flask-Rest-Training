from flask import Flask, jsonify, request
from CustomObjects import CustomObject1
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float
import os
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
# TO MAKE IT WORK, UNCOMMENT AND REGISTER ON mailtrap.io !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# from flask_mail import Mail, Message

# app registration
app = Flask(__name__)

# db registration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'dbname.db')

app.config['JWT_SECRET_KEY'] = 'super-secret'  # change this IRL, its jwt registration

# TO MAKE IT WORK, UNCOMMENT AND REGISTER ON mailtrap.io !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# app.config['MAIL_SERVER'] = 'smtp.mailtrap.io'
# app.config['MAIL_USERNAME'] = os.environ['MAIL_USERNAME'] # os.environ to zmienna ze sciezki PATH ustawionej w windowsowych zmiennych
# app.config['MAIL_PASSWORD'] = os.environ['MAIL_PASSWORD'] # os.environ to zmienna ze sciezki PATH ustawionej w windowsowych zmiennych


db = SQLAlchemy(app)
ma = Marshmallow(app) # needed for flask_marshmallow
jwt = JWTManager(app)
# TO MAKE IT WORK, UNCOMMENT AND REGISTER ON mailtrap.io !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# mail = Mail(app)

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


@app.route('/register', methods=['POST'])
def register():
    email = request.form['email']
    test = User.query.filter_by(email=email).first()
    if test: # if type is none, returns false
        return jsonify(message='that email has already been used'), 409
    else:
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        password = request.form['password']
        user = User(first_name=first_name, last_name=last_name, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return jsonify(message='User created successfully.'), 201



@app.route('/login', methods=['POST'])
def login():
    if request.is_json:
        email = request.json['email']
        password = request.json['password']
    else: # to have the option to login using both json and form args
        email = request.form['email']
        password = request.form['password']

    usr = User.query.filter_by(email=email, password=password).first()
    if usr: # if usr != None
        access_token = create_access_token(identity=email) # we can use email for that because for us email is set to be unique
        return jsonify(message='Login succeeded', access_token=access_token), 200 # 200 does not need to be written
    else:
        return jsonify(message='Bad email or password'), 401


# TO MAKE IT WORK, UNCOMMENT AND REGISTER ON mailtrap.io !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# @app.route('/retrieve_password/<string:email>', methods=['GET']) # retrieving forgotten password via email
# def retrieve_password(email: str):
#     user = user.query.filter_by(email=email).first()
#     if user:
#         msg = Message(f"Your password is {user.password}", sender="admin@mailadmina-api.com", recipients=[email])
#         mail.send(msg)
#         return jsonify(messate=f"Password has been sent to {email}")
#     else:
#         return jsonify(message='That mail does not exist'), 404





# CRUD ENDPOINTS
# CREATE
@app.route('/add_planet', methods=['POST'])
@jwt_required ## thats enough to ensure that user needs to be authorized with token 
def add_planet():
    planet_name = request.json['planet_name']
    planet = Planet.query.filter_by(planet_name=planet_name).first()
    
    if planet:
        return jsonify(f'There is already planet with this name ({planet_name})'), 409 # 409 means conflict
    else:
        planet_type = request.json['planet_type']
        home_star = request.json['home_star']
        mass = float(request.json['mass'])
        radius = float(request.json['radius'])
        distance = float(request.json['distance'])
        new_planet = Planet(planet_name=planet_name,
                            planet_type=planet_type,
                            home_star=home_star,
                            mass=mass,
                            radius=radius,
                            distance=distance)
        db.session.add(new_planet)
        db.session.commit()
        
        return jsonify(message=f'You created a planet {planet_name}'), 201 



# READ
@app.route('/planet_details/<int:planet_id>', methods=['GET'])
def planet_details(planet_id: int):
    planet = Planet.query.filter_by(planet_id=planet_id).first()
    if planet:
        result = planet_schema.dump(planet)
        return jsonify(result)
    else:
        return jsonify(message='That planet does not exist'), 404




# UPDATE
@app.route('/update_planet', methods=['PUT'])
@jwt_required
def update_planet():
    planet_name = request.form['planet_name']
    planet = Planet.query.filter_by(planet_name=planet_name).first()
    if planet:
        planet.planet_name = planet_name
        planet.planet_type = request.form['planet_type']
        planet.home_star = request.form['home_star']
        planet.radius = float(request.form['radius'])
        planet.distance = float(request.form['distance'])
        planet.mass = float(request.form['mass'])
        db.session.commit() # its enough to update the object in db

        return jsonify(message=f'You updated the planet {planet.planet_name}'), 202
    else:
        return jsonify('There is no such planet'), 404



# DELETE
@app.route('/delete_planet/<int:planet_id>', methods=['DELETE'])
@jwt_required
def delete_planet(planet_id: int):
    planet = Planet.query.filter_by(planet_id=planet_id).first()
    if not planet:
        return jsonify(message=f'Planet with id = {planet_id} does not exist'), 404
    else:
        db.session.delete(planet)
        db.session.commit()
        return jsonify(message=f'Planet with id = {planet_id} has been deleted'), 202




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