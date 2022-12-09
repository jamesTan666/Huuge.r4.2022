from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
from os import environ
import stripe
import uuid
from flask_cors import CORS
import requests
import webbrowser

 # This is your test secret API key.
stripe.api_key = 'sk_test_51KdqPTISYdBEvEEjARSCzRFLysecMlLMnxMBHoxyQRsrDKNrG88czsFtknxS90ZSpzVojRDN4TqqDH6HG51o7zf600zND3I9Ig'

# Setting cors policy
app = Flask(__name__)
cors = CORS(app, resources={r"*": {"origins": "*"}})

# Configurations
STRIPE_CALLBACK_URL='http://localhost:5003/'
ORDER_SERVICE_URL= 'http://order:5001/order/'
DB_URI=environ.get('dbURL')

# Config database connection
app.config['SQLALCHEMY_DATABASE_URI'] =  DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
Model=db.Model


# Models
class Payment(Model):
    __tablename__ = 'payment'

    paymentID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    orderID = db.Column(db.Integer, nullable=False)
    createdTime = db.Column(db.DateTime, nullable=False)
    totalPrice = db.Column(db.Integer, nullable=False)
    sessionID = db.Column(db.String(1000), nullable=True)
    token = db.Column(db.String(200), nullable=False)

# db.create_all()
# db.session.commit()
# Clients
def update_order_status(orderID,sessionStatus):
    # Convert payment status to order status

    print("Update order status order id:",orderID)
    orderStatus="2"

    if sessionStatus == "complete":
        orderStatus = "2"
    elif sessionStatus == "expired" or sessionStatus == "open":
        orderStatus = "1"

    requestBody={
        'status':orderStatus,
    }

    try:
        # Send request to order
        response = requests.put(ORDER_SERVICE_URL + str(orderID) , json = requestBody,timeout = 3)
        return response
    except Exception as e:
        print(e)

def create_checkout_session(totalPrice, orderID, token):
    try:
        # Three steps flow to create a stripe session
        productObject = stripe.Product.create(name=orderID)
        productId=productObject['id']

        price = stripe.Price.create(
            unit_amount=totalPrice,
            currency="sgd",
            product=productId
        )
        priceId=price['id']

        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': priceId,
                    "quantity": 1
                },
            ],
            mode='payment',
            success_url=STRIPE_CALLBACK_URL + '?token=' + token,
            cancel_url=STRIPE_CALLBACK_URL + '?token=' + token
        )

        return checkout_session
    except Exception as e:
        print(e)

#URL for the place order button then it will return the Stripe payment URL
@app.route("/payment", methods=['POST'])
def create_payment():

    # Prepare received data
    request_data = request.get_json()['data']
    orderID = request_data["order_id"]
    totalPrice = int(request_data["total_price"])*100
    print("This is the total price",totalPrice)
    createdTime=datetime.today()
    token=str(uuid.uuid4())

    stripeSession = create_checkout_session(totalPrice, orderID, token)

    if not stripeSession:
        return {
            'code':500,
            'message':'An error occurred while connecting to stripe'
        },500

    # Create payment model
    payment = Payment(orderID=orderID, createdTime=createdTime,totalPrice=totalPrice, token=token, sessionID = stripeSession['id'])

    try:
        db.session.add(payment)
        db.session.commit()
    except Exception as e:
        # Logging errors
        print(e)

        return jsonify(
            {
                "code": 500,
                "message": "An error occurred creating the transaction."
            }
        ), 500
    return jsonify(
    {
        "code": 201,
        "data": {
                'token':token,
                'order_id': orderID,
                'payment_url': stripeSession['url']
            }
    }
), 201


# URL for getting the status and update order service e.g. /payment?token={{token}}
@app.route("/payment", methods=['GET'])
def get_payment_result():
    # Prepare data

    token = request.get_json('token')
    print("token returnxx:",token)
    paymentObject = Payment.query.filter_by(token=token).first()
    paymentSession = stripe.checkout.Session.retrieve(paymentObject.sessionID)
    orderID = paymentObject.orderID
    print("orderID:",orderID)
    sessionStatus = paymentSession['status'];

    # Calling other services
    response = update_order_status(orderID, sessionStatus);

    if not response:
        return {
            'code':500,
            'message': 'An error occurred updating order status'
        },500

    return {
        'code':200,
        'data': {
            'order_id':orderID,
            'payment_url': paymentSession['url'],
            'status':sessionStatus
        }
    }


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=False)
