"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Planets, Favourites
import json
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

#Route
#app.register_Blueprint(api, url_prefix ="/api")

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

#1-GET methods
    #1.1-GET methods for user
@app.route('/users', methods=['GET'])
def handle_hello():

    users = User.query.all()
    if users == []:
        return jsonify({"msg":"users does not exist"}), 404
    
    response_body = list(map(lambda x:x.serialize(),users))

    return jsonify(response_body), 200 


    #1.2-GET methods for user favourites?
@app.route('/users/<string:user_name>', methods=['GET'])
def get_users_by_name(user_name):
    users = User.query.filter_by(name=user_name).all()

    if users:
        user_list = [{'id': user.id, 'name': user.name} for user in users]  
        return jsonify(user_list), 200
    else:
        return jsonify({"Error": "No se encontraron usuarios con ese nombre"}), 400

    #1.3-GET methods for characters 
@app.route('/character', methods=['GET'])       
def show_character():
    characters = Character.query.all()
    if characters == []:
        return jsonify({"msg":"These character does not exist"}), 404
    
    response_body = list(map(lambda x:x.serialize(),characters))

    return jsonify(response_body), 200 

#1.4-GET methods for single character
@app.route('/character/<int:people_id>', methods=['GET'])       
def show_single_character(people_id):
    characters = Character.query.filter_by(id = people_id).first() 
    if characters is None:
        return jsonify({"msg":"This character does not exist"}), 404
    
    return jsonify(characters.serialize()),200

#1.5 GET methods for planets
@app.route('/planets', methods=['GET'])       
def show_planets():
    planets = Planets.query.all()
    if planets == []:
        return jsonify({"msg":"These planets don't exist"}), 404
    
    response_body = list(map(lambda x:x.serialize(),planets))

    return jsonify(response_body), 200 


#1.6 GET methods for single planet
@app.route('/planet/<int:planet_id>', methods=['GET'])       
def show_single_planet(planet_id):
    planets = Planets.query.filter_by(id = planet_id).first() 
    if planets is None:
        return jsonify({"msg":"This planet does not exist"}), 404
    
    return jsonify(planets.serialize()),200

#2-POST methods
    #2.1-POST favourite planet method
@app.route('/user/<int:user_id>/favorite/planets/<int:planets_id>', methods=['POST'])       
def add_planets(user_id,planets_id):
    new_favourite_planets = Favourites(
        user_id = user_id,
        planets_id = planets_id
    )
    db.session.add(new_favourite_planets)
    db.session.commit()

    return jsonify({"msg": "Planet added to favourites"}), 200

#2.2-POST favourite character method
@app.route('/user/<int:user_id>/favorite/characters/<int:characters_id>', methods=['POST'])       
def add_characters(user_id,characters_id):
    new_favourite_character = Favourites(
        user_id = user_id,
        characters_id = characters_id
    )
    db.session.add(new_favourite_character)
    db.session.commit()

    return jsonify({"msg": "Character added to favourites"}), 200



#3-DELETE method
#3.1 DELETE favourite planet method
@app.route('/user/<int:user_id>/favorite/planets/<int:planets_id>', methods=['DELETE'])       
def delete_single_planet(user_id, planets_id):
    delete_planets = Favourites.query.filter_by( user_id = user_id,
        planets_id = planets_id).first() 
    if delete_planets is None:
        return jsonify({"msg":"This planet no longer exists"}), 404
    db.session.delete(delete_planets)
    db.session.commit()

    return jsonify({"msg": "Planet deleted from favourites"}), 200

#3.1 DELETE favourite character method
@app.route('/user/<int:user_id>/favorite/characters/<int:characters_id>', methods=['DELETE'])       
def delete_single_character(user_id, characters_id):
    delete_character = Favourites.query.filter_by( user_id = user_id,
        characters_id = characters_id).first() 
    if delete_character is None:
        return jsonify({"msg":"This character does not exist"}), 404
    db.session.delete(delete_character)
    db.session.commit()

    return jsonify({"msg": "Planet deleted from favourites"}), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
