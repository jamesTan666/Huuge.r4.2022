import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import date, datetime
import json
from os import environ

# Intialize flask application - __name__ variable to let Flask intelligently configure other parts of our application
app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/gym_delivery'
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)

CORS(app)



class Delivery(db.Model):
    __tablename__ = 'delivery'

    deliveryID = db.Column(db.Integer, primary_key=True)
    driverID = db.Column(db.Integer, nullable = True)
    driverName = db.Column(db.String(32), nullable = True)
    dateCreated = db.Column(db.DateTime, nullable=False, default=datetime.now)
    deliveryStatus = db.Column(db.String(10), nullable=False, default='0')
    orderID = db.Column(db.String(32), nullable=False)

    # def __init__(self, deliveryID, driverName, dateCreated, deliveryStatus, orderID):
    #     self.deliveryID = deliveryID
    #     self.driverName = driverName
    #     self.dateCreated = dateCreated
    #     self.deliveryStatus = deliveryStatus
    #     self.orderID = orderID

    def json(self):
        return {"deliverID" : self.deliveryID, "driverID" : self.driverID, "driverName": self.driverName, "dateCreated" : self.dateCreated, "deliveryStatus": self.deliveryStatus, "orderID" : self.orderID}


# get all delivery records
@app.route('/delivery', methods=['GET'])
def get_all():
    delivery_list = Delivery.query.all()
    if len(delivery_list):
        return jsonify(
            {
                "code": 200,
                "data" : {
                    "delivery" : [ delivery.json() for delivery in delivery_list]
                }
            }
        )
    return jsonify(
        {
            "code" : 404,
            "message" : "There is no delivery."
        }
    ), 404


# get specific delivery record based on order ID
# this is for customer to check delivery status based on order ID (GET)
@app.route("/delivery/<string:orderID>")
def find_by_order_id(orderID):
    order = Delivery.query.filter_by(orderID=orderID).first()
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
                "orderID": orderID
            },
            "message": "Order not found."
        }
    ), 404


#
@app.route("/delivery/status", methods=['POST'])
def find_by_status_custid():
    data = request.get_json()

    if data['cust_id']:
        order = Delivery.query.filter_by(driverID=data['cust_id'], deliveryStatus=data['deliveryStatus']).all()
        if order:
            return jsonify(
                {
                    "code": 200,
                    "data" : {
                    "delivery" : [ delivery.json() for delivery in order]
                    }
                }
            )
        return jsonify(
            {
                "code": 404,
                "data": {
                    "driverID": data['cust_id']
                },
                "message": "Orders not found for drivers."
            }
        ), 404


# =====================================================================
#
#    CREATE DELIVERY RECORD
#       DOCUMENTATIONS: Look at slide 8 (proposal slides) After payment is successful, create delivery record with the orderID
#                       This is without a driver assigned yet, because driver have to pick one and the status is set to 0
#                       Delivery status are 0 = preparing, 1 = out for delivery and 2 = delivered
#       PARAMETERS: OrderID
#       RETURN:
#
# ====================================================================
@app.route("/delivery", methods=['POST'])
def create_delivery():

    data = request.json.get('data')
    orderID=data['order_id']
    print("OrderID",orderID)
    delivery = Delivery(deliveryStatus='0', orderID=orderID)

    try:
        db.session.add(delivery)
        db.session.commit()
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "message": "An error occurred while creating the order. " + str(e)
            }
        ), 500

    print(json.dumps(delivery.json(), default=str)) # convert a JSON object to a string and print
    print()

    return jsonify(
        {
            "code": 201,
            "data": delivery.json()
        }
    ), 201



# =====================================================================
#
#    UPDATE DELIVERY RECORD
#       DOCUMENTATIONS: Look at slide 13 (proposal slides) After driver delivered the item, driver will select the delivery record to update the ID
#       PARAMETERS: OrderID
#
# ====================================================================
@app.route("/delivery/<string:orderID>", methods=['PUT'])
def update_delivery(orderID):
    try:
        delivery = Delivery.query.filter_by(orderID=orderID).first()
        if not delivery:
            return jsonify(
                {
                    "code": 404,
                    "data": {
                        "orderID": orderID
                    },
                    "message": "Order not found."
                }
            ), 404

        # update status
        data = request.get_json()
        if data['deliveryStatus'] and  data['driverName']:
            delivery.deliveryStatus = data['deliveryStatus']
            delivery.driverName = data['driverName']
            delivery.driverID = data['driverID']
            db.session.commit()
            return jsonify(
                {
                    "code": 200,
                    "data": delivery.json()
                }
            ), 200
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "orderID": orderID
                },
                "message": "An error occurred while updating the order. " + str(e)
            }
        ), 500

# our application behind an if guard - this ensure that we don't start up webservers if we ever import this script into another one
if __name__ == '__main__':
    print("This is flask for " + os.path.basename(__file__) + ": manage delivery ...")
    app.run(host='0.0.0.0', port=5002, debug=True)
