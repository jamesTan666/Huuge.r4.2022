#from crypt import methods
from email.policy import default
from ssl import DefaultVerifyPaths
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os, sys
from os import environ
from flask import Flask, request, jsonify
#from itsdangerous import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}
db = SQLAlchemy(app)
cors = CORS(app, resources={r"*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'

class Cart(db.Model):
    __tablename__ = 'cart'

    custId = db.Column(db.String(10), primary_key=True)
    cartItems = db.Column(db.JSON, default={})

    def __init__(self,custId,cartItems):
        self.custId = custId
        self.cartitems = cartItems
    def json(self):
        return {"custId" : self.custId, "cartItems" : self.cartItems}


@app.route("/newCart/<string:custId>", methods=['POST'])
def newCart(custId):
    if (Cart.query.filter_by(custId=custId).first()):
        return jsonify({
            "code" : 400,
            "message" : "Cart already create for user " + custId
        })
    emptyCart = jsonify({
        "cartItems" : []
    })
    cart = Cart(custId,emptyCart)
    try:
        db.session.add(cart)
        db.session.commit()
    except:
        return jsonify({
            "code" : 500,
            "message" : "An error occurred creating the cart for user " + custId
        })

    return jsonify({
        "code" : 201,
        "data" : cart.json()
    })

@app.route("/cart/<string:custId>") #get
def userCart(custId):
    userCartItem = Cart.query.filter_by(custId=custId).first()
    if userCartItem:
        return jsonify(
            {
                "code" : 200,
                "data" : userCartItem.json()
            }
        )

    return jsonify({
        "code" : 400,
        "message" : "No cart found for user" + custId
    })

@app.route("/updateCart/<string:custId>", methods=['PUT'])
def updateCart(custId):
    data = request.get_json()
    cart = Cart.query.filter_by(custId=custId).first()
    print("This is my data",data)
    cart.cartItems = data["cartItems"]
    try:
        db.session.commit()
    except:
        return jsonify({
            "code" : 500,
            "message" : "An error occured updating the cart"
        })
    return jsonify({
        "code" : 201,
        "data" : data
    })
if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) +
          " for placing an order...")
    app.run(host="0.0.0.0", port=5007, debug=True)
