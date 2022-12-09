#!/usr/bin/env python3
# The above shebang (#!) operator tells Unix-like environments
# to run this file as a python3 script

import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from os import environ
from datetime import date, datetime
from flask_cors import CORS

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/gym_orders'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
##DB_URI='mariadb+mariadbconnector://test:test@localhost:3306/gym_order'
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')
#app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
CORS(app)

class Order(db.Model):
    __tablename__ = 'order'

    order_id = db.Column(db.Integer, primary_key=True)
    cust_id = db.Column(db.String(32), nullable=False)
    date_created = db.Column(db.String(32), nullable=False, default=datetime.now)
    total_price = db.Column(db.Float(11), nullable=False)
    delivery_address = db.Column(db.String(32), nullable=False)
    status = db.Column(db.String(32), nullable=False)
    modified = db.Column(db.DateTime, nullable=False,
                         default=datetime.now, onupdate=datetime.now)

    def json(self):
        orderd = {
             'order_id': self.order_id,
             'cust_id': self.cust_id,
             'date_created': self.date_created,
             'total_price': self.total_price,
             'delivery_address': self.delivery_address,
             'status': self.status,
             'modified': self.modified}

        orderd['order_item'] = []

        for oi in self.order_item:
            orderd['order_item'].append(oi.json())

        return orderd

class Order_item(db.Model):
    __tablename__ = 'order_item'

    item_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.ForeignKey(
        'order.order_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)

    product_id = db.Column(db.String(13), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)


    order = db.relationship('Order', backref='order_item')
    # db.relationship('Order', primaryjoin='Order_item.order_id == Order.order_id', backref='order_item')

    def json(self):
      return {'item_id': self.item_id,
             'order_id': self.order_id,
             'product_id': self.product_id,
              'quantity': self.quantity}



@app.route("/order")
def get_all():
    orderlist = Order.query.all()
    if len(orderlist):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "orders": [order.json() for order in orderlist]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no orders."
        }
    ), 404


@app.route("/order/uid/<string:cust_id>")
def find_by_cust_id(cust_id):

    orderList = Order.query.filter_by(cust_id=cust_id).all()
    if orderList:
        return jsonify(
            {
                "code": 200,
                "data": [order.json() for order in orderList]
            }
        )
    return jsonify(
        {
            "code": 404,
            "data": {
                "id": cust_id
            },
            "message": "Order not found."
        }
    ), 404



@app.route("/order/<string:order_id>")
def find_by_order_id(order_id):

    order = Order.query.filter_by(order_id=order_id).first()
    if order:
        return jsonify(
            {
                "code": 200,
                "data": order.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "data": {
                "order_id": order_id
            },
            "message": "Order not found."
        }
    ), 404

@app.route("/order/status/<string:status>", methods=['POST'])#POST
def find_status(status):

    orderlist = Order.query.filter_by(status=status).all()
    if len(orderlist):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "orders": [order.json() for order in orderlist]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no orders."
        }
    ), 404

@app.route("/order", methods=['POST'])
def create_order():

    cust_id = request.json.get('custID')
    cart_items = request.json.get('cartItems')
    total_price = 0
    if cust_id:
        delivery_address=request.json.get("delivery")
    else:
        delivery_address=""
    status="0"

    for item in cart_items:
        total_price += item['price'] * item['quantity']

        order = Order(
                    cust_id = cust_id,
                    total_price=total_price,
                    delivery_address=delivery_address,
                    status=status)


        order.order_item.append(Order_item(product_id=item['productID'], quantity=item['quantity']))

    try:
        db.session.add(order)
        db.session.commit()
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "message": "An error occurred while creating the order. " + str(e)
            }
        ), 500

    return jsonify(
        {
            "code": 201,
            "data": order.json()
        }
    ), 201


@app.route("/order/<string:order_id>", methods=['PUT'])
def update_order(order_id):
    try:
        order = Order.query.filter_by(order_id=order_id).first()
        if not order:
            return jsonify(
                {
                    "code": 404,
                    "data": {
                        "order_id": order_id
                    },
                    "message": "Order not found."
                }
            ), 404

        # update status
        data = request.get_json()
        if data['status']:
            order.status = data['status']
            db.session.commit()
            return jsonify(
                {
                    "code": 201,
                    "data": order.json()
                }
            ), 200
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "order_id": order_id
                },
                "message": "An error occurred while updating the order. " + str(e)
            }
        ), 500

@app.route("/order/delivery_address/<string:order_id>", methods=['PUT'])
def update_delivery(order_id):
    try:
        order = Order.query.filter_by(order_id=order_id).first()
        if not order:
            return jsonify(
                {
                    "code": 404,
                    "data": {
                        "order_id": order_id
                    },
                    "message": "Order not found."
                }
            ), 404

        # update status
        data = request.get_json()
        if data['delivery_address']:
            order.delivery_address = data['delivery_address']
            db.session.commit()
            return jsonify(
                {
                    "code": 201,
                    "data": order.json()
                }
            ), 200
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "order_id": order_id
                },
                "message": "An error occurred while updating the order. " + str(e)
            }
        ), 500


if __name__ == '__main__':
    print("This is flask for " + os.path.basename(__file__) + ": manage orders ...")
    app.run(host='0.0.0.0', port=5001, debug=True)
