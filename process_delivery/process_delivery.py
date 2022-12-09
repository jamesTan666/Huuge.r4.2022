
import os, sys
from os import environ
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import date, datetime
# import amqp_setup
# import pika
import json

from invokes import invoke_http
# from delivery.microservices import delivery
# from delivery.microservices import updateOrderStatus
from microservices import *

# Intialize flask application - __name__ variable to let Flask intelligently configure other parts of our application
app = Flask(__name__)

CORS(app)

# =====================================================================
#
#    PROCESS DELIVERY
#       DOCUMENTATIONS: This step will be when driver retrieves the list of orders that are payment success, once selects the the order -> it will trigger the update delivery, update order status and update driver status
#          This function should be used when driver accepts and completes the orders
# preparing (0), delivering (1), delivered (2)
# delivering (3), delivered (4)
# ====================================================================
@app.route("/process-delivery", methods=['POST'])
def process_delivery():

    if request.is_json: #ensure data format is json
        try:
            dataSet = request.get_json() #get json passed in
            print("\n Received an order in Json:", dataSet)


            deliveryUpdateStatus = {
                'order_id':dataSet["order_id"],
                'deliveryStatus':dataSet["deliveryStatus"],
                'driverName':dataSet["driverName"],
                'driverID':dataSet["driverID"]
            }



            if dataSet["deliveryStatus"] == "1":
                # update order status to 3 (delivering) when is driver status delivering (1)
                print("deliveryUpdateStatus:",deliveryUpdateStatus)
                deliveryResult = delivery(deliveryUpdateStatus)
                orderResult = updateOrderStatus(dataSet["order_id"],{"status":3})
                print(deliveryResult)
                print(orderResult)

                return jsonify({
                    "code" : 201,
                    "message" : "Process delivery successful!",
                    "deliveryResult" : deliveryResult,
                    "orderResult" : orderResult
                }), 201

            elif dataSet["deliveryStatus"] == "2":
                # update order status to 4 (delivered) when is driver status delivered (2)
                deliveryResult = delivery(deliveryUpdateStatus)
                orderResult=updateOrderStatus(dataSet["order_id"],{"status":4})
                print(deliveryResult)
                print(orderResult)

                return jsonify({
                    "code" : 201,
                    "message" : "Process delivery successful!",
                    "deliveryResult" : deliveryResult,
                    "orderResult" : orderResult
                }), 201

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



# Execute this program if it is run as a main script (not by 'import')
if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) +
          " for placing an order...")
    app.run(host="0.0.0.0", port=5200, debug=True)
