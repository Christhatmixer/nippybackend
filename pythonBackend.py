import stripe
import sys
import json
import requests
from flask import Flask, render_template, request, jsonify


stripe.api_key = "sk_live_gSZhEw9uwQwEyEpLEftrbGzn"

app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
def pay():
    data = request.json
    token = data["stripeToken"]
    name = data["shipping"]["name"]
    city = data["shipping"]["address"]["city"]
    lineOne = data["shipping"]["address"]["line1"]
    postalCode = data["shipping"]["address"]["postal_code"]
    state = data["shipping"]["address"]["state"]
    charge = stripe.Charge.create(
    amount=data["amount"],
    currency='usd',
    receipt_email= data["receipt_email"],
    source=token,
    shipping={"name":name,"address":{"city":city,"line1": lineOne,"state":state,
                                     "postal_code":postalCode
                                     }}
      
    )

    return "hello chris"
@app.route("/order", methods=['GET', 'POST'])
def order():
    data = request.json
    token = data["stripeToken"]
    name = data["shipping"]["name"]
    city = data["shipping"]["address"]["city"]
    lineOne = data["shipping"]["address"]["line1"]
    postalCode = data["shipping"]["address"]["postal_code"]
    state = data["shipping"]["address"]["state"]
    
    order = stripe.Order.create(
 
      currency="usd",
       # obtained with Stripe.js
      email=data["receipt_email"],

       items=data["items"],
        shipping={"name":name,"address":{"city":city,"line1": lineOne,"state":state,
                                         "postal_code":postalCode
                                         }}
    )
    orderID = stripe.Order.retrieve(order.id)
    order.pay(source=data["stripeToken"])
    return("order done")

@app.route("/getProducts", methods=['GET', 'POST'])
def showProducts():
    products = stripe.Product.list(limit=10)
    return jsonify(products)

@app.route("/updateProducts", methods=['GET','POST'])
def updateProducts():
    data = requests.get("https://api.bigcartel.com/Nippy/products.json")
    
    for product in data.json():
        name = product["name".replace(" ","")]
        try:
            stripe.Product.create(
                name=name.replace(" ",""),
                type='good',
                id = name.replace(" ","").replace("*","u"),
                attributes = ["size","color"]
            )
        except:


            print("product already exist")
        for option in product["options"]:
            if option["sold_out"] == True:
                print("item is sold out")
            else:
                
                price = option["price"]
                variants = option["name"].split("-")
                size = variants[1].replace(" ","")
                color = variants[0]
                productID = name.replace(" ","").replace("*","u") + color + size.strip()
                
                try:
                    stripe.SKU.create(
                        id=productID,
                        currency='usd',
                        inventory={
                            'type': 'finite',
                            'quantity': 500,
                        },
                        price= int(price * 100),
                        product=name.replace(" ","").replace("*","u"),
                        attributes={
                            'size': size.strip(),
                            'color': color,
                        },
                    )
                except:
                    print("product already exist")
                    sku = stripe.SKU.retrieve(productID)
                    sku.price = int(price * 100)
                    sku.save()
    return "Update Successful"
                

            
    
    
if __name__ == '__main__':
    app.run()
