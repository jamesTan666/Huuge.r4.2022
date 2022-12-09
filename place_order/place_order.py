import amqp_setup
import pika
import json
import time
from crypt import methods
import re
from unittest import result
#from black import err
from flask import Flask, request, jsonify
from flask_cors import CORS
import os, sys
#from itsdangerous import json
from microservices import *
app = Flask(__name__)

cors = CORS(app, resources={r"*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'

'''
Order Status --> 5 Statuses
0 - orderCreated
1 - paymentUnsuccessful
2 - paymentSuccessful
3 - delivering
4 - delivered
'''


@app.route("/place_order", methods=["POST"])
def place_order():

    if request.is_json: #ensure data format is json
        try:
            order = request.get_json()['data'] #get json passed in
            print("\n Received an order in Json:", order)
            print(order)
            #invoking Order------
            orderResult = processOrder(order)
            #activity(orderResult)
            if orderResult["data"]["status"] != "0":
                #invoking fails
                return jsonify(orderResult), orderResult['Status']
            #Order successful--------

            #invoking payment
            print("This is the order", orderResult)

            paymentResult = payment(orderResult,"POST")
            print("This is payment result", paymentResult)
            if paymentResult["code"] == 500:
                #invoking fails
                statusResult=updateOrderStatus(orderResult["data"]["order_id"],{"status":1})
                #return jsonify(paymentResult),paymentResult["code"]
                print(statusResult)
                return jsonify(statusResult)
            elif paymentResult["code"] == 201:
                return jsonify({
                    "orderResult" : orderResult,
                    "paymentResult" : paymentResult,
                    "order" : order
                })
            else:
                return jsonify({
                    "code" : 500,
                    "message" : "place_order payment error"
                }), 500


        except Exception as e:
            #catch if any error occurs
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_fname.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line" + str(exc_tb.tb_lineno)
            print(ex_str)
            return jsonify({
                "code" : 500,
                "message" : "place_order internal error: " + ex_str
            }), 500
    else:
        return jsonify({
            "code" : 400,
            "message" : "Invalid JSON input: " + str(request.get_data())
        }), 400

@app.route("/process_payment", methods=["POST"])
def process_payment():
    #payment successful invokes delivery
    print("Item receive in process payment ",)
    paymentResult = request.get_json("data")["paymentResult"]
    orderResult = request.get_json("data")["orderResult"]
    order = request.get_json("data")["order"]
    print("This is payment result",paymentResult)
    print("This is order result ", orderResult)
    print("This is order ", order)
    token = paymentResult["data"]["token"]
    result  = payment(token,"GET")
    '''
    Status: expired, complete, open
    payment status: paid, unpaid
    '''
    print("ressult:",result)
    status = result["data"]["status"]
    startTime = time.time()
    while(status != "complete"):
        timePassed = time.time()-startTime
        if(timePassed>60):
            statusResult=updateOrderStatus(orderResult["data"]["order_id"],{"status":1})
            return jsonify(statusResult)
        time.sleep(5)
        result = payment(token ,"GET")
        status = result["data"]["status"]


    statusResult=updateOrderStatus(orderResult["data"]["order_id"],{"status":2})
    #delivery(orderResult["orderID"])
    #paymentResult["Delivery"] = "Scheduling Delivery..." #may change
    #return jsonify(payme  ntResult),paymentResult["code"]
    print(statusResult)

    if statusResult["code"] == 201: #statusResult
        print("Items to be updated:",orderResult["data"]["order_item"])
        updateInventoryResult = inventory(order["cartItems"])
        if(updateInventoryResult["code"] == 200):

            deliveryResult=delivery(orderResult)

            return jsonify(
                {
                    "code" : 200,
                    "data" :{
                        "status" :deliveryResult,
                        "paymentURL" : paymentResult['data']['payment_url']
                    }
                }
            )
    return jsonify(statusResult)

if __name__ == '__main__':
    print("This is flask for " + os.path.basename(__file__) + ": manage orders ...")
    app.run(host='0.0.0.0', port=5100, debug=True)
