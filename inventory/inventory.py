from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
import os, sys
from os import environ
from flask_cors import CORS


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/gym_inventory'

db = SQLAlchemy(app)
CORS(app)


class Inventory(db.Model):
    __tablename__ = 'inventory'

    productID = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    product_type = db.Column(db.String(64), nullable=False)
    price = db.Column(db.Float(precision=2), nullable=False)
    quantity = db.Column(db.Integer)

    # def __init__(self, productID, name, product_type, price, quantity):
    #     self.productID = productID
    #     self.name = name
    #     self.product_type = product_type
    #     self.price = price
    #     self.quantity = quantity

    def json(self):
        return {"productID": self.productID, "name": self.name, "product_type": self.product_type, "price": self.price, "quantity": self.quantity}

@app.route("/inventory")
def get_all():

    inventorylist = Inventory.query.all()
    if len(inventorylist):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "inventories": [inventory.json() for inventory in inventorylist]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There is no inventory."
        }
    ), 404

@app.route("/inventory/<int:productID>")
def find_by_productID(productID):
    equipment = Inventory.query.filter_by(productID=productID).first()
    if equipment:
        return jsonify(
            {
                "code": 200,
                "data": equipment.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "Equipment not found."
        }
    ), 404


@app.route("/inventory", methods=['POST'])
def create_item():

    data = request.get_json()
    
    inventory = Inventory(name=data['name'], product_type=data['product_type'], price=data['price'], quantity=data['quantity'])

    try:
        db.session.add(inventory)
        db.session.commit()
    except:
        return jsonify(
            {
                "code": 500,
                "message": "An error occurred creating the inventory."
            }
        ), 500

    return jsonify(
        {
            "code": 201,
            "data": inventory.json()
        }

    ), 201


## MAY NOT BE IN USED
@app.route("/inventory/<int:productID>", methods=['POST'])
def add_inventory(productID):

    if (Inventory.query.filter_by(productID=productID).first()):
        return jsonify(
            {
                "code": 400,
                "data": {
                    "productID": productID
                },
                "message": "Equipment already exists."
            }
        ), 400

    data = request.get_json()
    inventory = Inventory(productID, **data)

    try:
        db.session.add(inventory)
        db.session.commit()
    except:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "productID": productID
                },
                "message": "An error occurred creating the inventory."
            }
        ), 500

    return jsonify(
        {
            "code": 201,
            "data": inventory.json()
        }

    ), 201



@app.route("/inventory", methods=['PUT'])
def update_equipment():
    data = request.get_json()
    returnData = []
    print("Data Received xx:",type(data))
    for item in data:
        print("Processing item:",item )
        productID = item['productID']
        equipment = Inventory.query.filter_by(productID=productID).first()
        if equipment:
            if item['quantity']:
                equipment.quantity = equipment.quantity - int(item["quantity"])
                returnData.append(equipment.json())
                db.session.commit()

        else:
            return jsonify(
                {
                    "code": 404,
                    "data": {
                        "productID": productID
                    },
                    "message": "Equipment not found."
                }
            ), 404
    return jsonify(
        {
            "code": 200,
            "data": returnData
        }
    )


@app.route("/add-inventory/<int:productID>", methods=['PUT'])
def add_equipment(productID): #Updates current inventory
    equipment = Inventory.query.filter_by(productID=productID).first()
    if equipment:
        data = request.get_json()
        if data['quantity']:
            equipment.quantity = equipment.quantity + data['quantity'] 
        db.session.commit()
        return jsonify(
            {
                "code": 201,
                "data": equipment.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "data": {
                "productID": productID
            },
            "message": "Equipment not found."
        }
    ), 404


@app.route("/deduct-inventory/<int:productID>", methods=['PUT'])
def deduct_equipment(productID): #Updates current inventory
    equipment = Inventory.query.filter_by(productID=productID).first()
    if equipment:
        data = request.get_json()
        if data['quantity']:
            equipment.quantity = equipment.quantity - data['quantity'] 
        db.session.commit()
        return jsonify(
            {
                "code": 201,
                "data": equipment.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "data": {
                "productID": productID
            },
            "message": "Equipment not found."
        }
    ), 404

@app.route("/inventory/<int:productID>", methods=['DELETE'])
def delete_equipment(productID):
    equpiment = Inventory.query.filter_by(productID=productID).first()
    if equpiment:
        db.session.delete(equpiment)
        db.session.commit()
        return jsonify(
            {
                "code": 201,
                "data": {
                    "productID": productID
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "data": {
                "productID": productID
            },
            "message": "Equipment not found."
        }
    ), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5006, debug=True)
