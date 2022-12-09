from flask import Flask, request, jsonify
from flask_cors import CORS

import os, sys
from os import environ

import requests
from invokes import invoke_http

import amqp_setup
import pika
import json
'''
Order api url (POST)
Create a new order with all the items in CartJson + Customer details
Return the status of order
'''
order_URL = environ.get('order_URL')

'''
Payment api url (POST)
Take in orderID, total price
Return successful/Unsuccessful
'''
payment_URL = environ.get('payment_URL')

'''
Delivery api url (POST)
Create the delivery order only if payment is successful
'''
delivery_URL = environ.get('delivery_URL')
inventory_URL = environ.get('inventory_URL')

def updateOrderStatus(id,status):
    print("\n\n--------Update order microservice--------")
    status_URL=order_URL+"/"+str(id)
    #print(status_URL)
    result = invoke_http(status_URL,method="PUT",json=status)
    #print(result)
    return result

def processOrder(order):
    print("\n\n--------Invoking order microservice--------")
    result = invoke_http(order_URL,method="POST",json=order)
    print("Order result: ", result)
    #if result["OrderStatus"] != 0:
    if result["data"]['status']!="0":

        # Inform the error microservice
        #print('\n\n-----Invoking error microservice as order fails-----')
        print('\n\n-----Publishing the (order error) message with routing_key=order.error-----')

        # invoke_http(error_URL, method="POST", json=order_result)
        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="order.error",
            body="order error", properties=pika.BasicProperties(delivery_mode = 2))
        # make message persistent within the matching queues until it is received by some receiver
        # (the matching queues have to exist and be durable and bound to the exchange)

        # - reply from the invocation is not used;
        # continue even if this invocation fails

        print("\nOrder status ({:d}) published to the RabbitMQ Exchange:".format(
            404), result)

        # 7. Return error
        return {
            "code": 500,
            "data": {"order_result": result},
            "message": "Order creation failure sent for error handling."
        }


    # 4. Record new order
    # record the activity log anyway
    #print('\n\n-----Invoking activity_log microservice-----')
    print('\n\n-----Publishing the (order info) message with routing_key=order.info-----')

    # invoke_http(activity_log_URL, method="POST", json=order_result)
    amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="order.info",
        body="order successful")

    print("\nOrder published to RabbitMQ Exchange.\n")
    return result

def payment(paymentDetails,m):
    print("\n\n--------Invoking payment microservice--------")
    result = invoke_http(payment_URL,method=m,json=paymentDetails)
    print("Payment result: ", result)
    # if result["data"]["status"] == "1":
    #     result = error("Order",paymentDetails)
    return result

def inventory(items):
    print("\n\n--------Invoking Inventory microservice--------")
    print("put")
    result = invoke_http(inventory_URL,method="PUT",json=items)
    print("Update inventory result: ", result)
    # if result["data"]["status"] == "1":
    #     result = error("Order",paymentDetails)
    return result

def delivery(deliveryDetails):
    print("\n\n--------Invoking Delivery microservice--------")
    result = invoke_http(delivery_URL,method="POST",json=deliveryDetails)
    print("Delivery result: ", result)

    if result['code'] != 201:
        # Inform the error microservice
        #print('\n\n-----Invoking error microservice as order fails-----')
        print('\n\n-----Publishing the (order error) message with routing_key=order.error-----')

        # invoke_http(error_URL, method="POST", json=order_result)
        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="order.error",
            body="delivery error", properties=pika.BasicProperties(delivery_mode = 2))
        # make message persistent within the matching queues until it is received by some receiver
        # (the matching queues have to exist and be durable and bound to the exchange)

        # - reply from the invocation is not used;
        # continue even if this invocation fails

        print("\nOrder status ({:d}) published to the RabbitMQ Exchange:".format(
            404), result)

        # 7. Return error
        return {
            "code": 500,
            "data": {"order_result": result},
            "message": "Order creation failure sent for error handling."
        }


    # 4. Record new order
    # record the activity log anyway
    #print('\n\n-----Invoking activity_log microservice-----')
    print('\n\n-----Publishing the (order info) message with routing_key=order.info-----')

    # invoke_http(activity_log_URL, method="POST", json=order_result)
    amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="order.info",
        body="delivery sucessful")

    print("\nOrder published to RabbitMQ Exchange.\n")
    return result
