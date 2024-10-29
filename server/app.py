#!/usr/bin/env python3

from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response,jsonify
from flask_restful import Api, Resource
import os


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def index():
    return '<h1>Code challenge</h1>'


@app.route('/restaurants')
def get_restaurants():
    restaurants = Restaurant.query.all()
    body = jsonify([restaurant.to_dict() for restaurant in restaurants])  # Use the new to_dict method

    return make_response(body, 200)


@app.route('/restaurants/<int:id>', methods=['GET', 'DELETE'])
def get_by_id(id):
    restaurant = Restaurant.query.filter(Restaurant.id == id).first()

    if restaurant is None:
        return {"error":"Restaurant not found"}, 404

    if request.method == 'GET':
        body = restaurant.to_dict()
        return make_response(body, 200)
    
    elif request.method == 'DELETE':
        db.session.delete(restaurant)
        db.session.commit()
        return "", 204 ## to return empty body and status code


@app.route('/pizzas')
def get_pizzas():
    pizzas = Pizza.query.all()

    results = []
    for pizza in pizzas:
        results.append(pizza.to_dict())

    return make_response(results, 200)    

@app.route('/restaurant_pizzas', methods=['POST'])
def add_restaurant_pizzas():
    data = request.get_json()

    # Input validations 
    if not data or 'price' not in data or 'pizza_id' not in data or 'restaurant_id' not in data:
        return {"error": "validation errors"}, 400

    price = data['price']
    pizza_id = data['pizza_id']
    restaurant_id = data['restaurant_id']

    # Check if the pizza and restaurant exist
    pizza = Pizza.query.get(pizza_id)
    restaurant = Restaurant.query.get(restaurant_id)

    if pizza is None or restaurant is None:
        return {"error": "Pizza or restaurant not found"}, 404

    try:
        # Create a new RestaurantPizza instance
        added_rest_pizza = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)
        db.session.add(added_rest_pizza)
        db.session.commit()
        
        # Response
        response_body = {
            "id": added_rest_pizza.id,
            "pizza": {
                "id": pizza.id,
                "name": pizza.name,
                "ingredients": pizza.ingredients
            },
            "pizza_id": added_rest_pizza.pizza_id,
            "price": added_rest_pizza.price,
            "restaurant": {
                "address": restaurant.address,
                "id": restaurant.id,
                "name": restaurant.name
            },
            "restaurant_id": added_rest_pizza.restaurant_id,
        }

        return make_response(jsonify(response_body), 201)
    
    except Exception as e:
        db.session.rollback()  # Rollback session on error
        return {"error": str(e)}, 400  # Return error message and status code

if __name__ == '__main__':
    app.run(port=5555, debug=True)
