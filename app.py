import os
# Allow python code to communicate with different Operating systems
from flask import *
import pymysql
import pymysql.cursors
from flask_cors import CORS
app= Flask(__name__)
# allow requests from external origins
CORS(app) 
# Configure our upload folder.
app.config['upload_folder']='static/images'

@app.route('/api/signup',methods=['POST'])
def signup():  
    # extract values posted in the request and store them in variables.
    username= request.form['username']
    email=request.form['email']
    password=request.form['password']
    phone=request.form['phone']

    # connect to the database
    connection=pymysql.connect(host='localhost',user='root',password='',database='dailyyoghurt_kiboko')

    # Initialize the connection.
    cursor= connection.cursor()

    # do the sql query to insert the data of the columns
    sql='insert into users(username,email,password,phone) values(%s,%s,%s,%s)'

    # Create data to replace placeholders
    data=(username,email,password,phone)

    # Execute the sql and the data together using our cursor.
    cursor.execute(sql,data)

    # we need to save changes 
    connection.commit()

    return jsonify({'success':'Thank you for joining'})

@app.route('/api/signin',methods=['POST'])
def signin():
    username=request.form['username']
    password=request.form['password']

    connection=pymysql.connect(host='localhost',user='root', password='',database='dailyyoghurt_kiboko')
    cursor=connection.cursor(pymysql.cursors.DictCursor)
    sql='select * from users where username=%s and password=%s'
    data=(username,password)
    cursor.execute(sql,data)
    count=cursor.rowcount  
    #  tells if has returned row
    if count==0:
        return jsonify({'message':'Login Failed'})
    else:
     # There's fetchall and fetchmany.......Fetchall-Get everything from DB.......Fetchmany- Get several things from DB
        user=cursor.fetchone()
    # remove the password key.
        del user['password']
        # also: user.pop('password')
        return jsonify({'message':'Login Successful','user':user})
# add product  
# product route 
@app.route('/api/add_products',methods=['POST'])
# Function
def add_products():
    # extract values
    product_name=request.form['product_name']
    product_description=request.form['product_description']
    product_cost=request.form['product_cost']
    product_photo=request.files['product_photo']     
    # get the image file name
    filename=product_photo.filename
    # specify comp path where image be saved
    photo_path=os.path.join(app.config['upload_folder'],filename)
    # save the path
    product_photo.save(photo_path)
    # Initialize connection
    connection=pymysql.connect(host='localhost',user='root', password='',database='dailyyoghurt_kiboko')
    # Manipulate database
    cursor=connection.cursor()
    # Input insert query
    sql='insert into products_details(product_name,product_description,product_cost,product_photo) values(%s,%s,%s,%s)'
    # Add data to rerplace placeholders
    data=(product_name,product_description,product_cost,filename)
    # Execute the query
    cursor.execute(sql,data)
    # Make changes 
    connection.commit()
    # Show user a message/response.
    return jsonify({'message':'Product Added Successfully'})
# get productsg
@app.route('/api/get_product_details')
def getproduct():
    # connection
    connection=pymysql.connect(host='localhost',user='root', password='',database='dailyyoghurt_kiboko')
    # create a cursor object
    cursor=connection.cursor(pymysql.cursors.DictCursor)
    # sql query
    sql='select * from products_details'
    # execute your sql
    cursor.execute(sql)
    # get products in form of a dictionary
    products=cursor.fetchall()
    # return products
    return jsonify({'products':products})
 # Mpesa Payment Route 
import requests
import datetime
import base64
from requests.auth import HTTPBasicAuth

@app.route('/api/mpesa_payment', methods=['POST'])
def mpesa_payment():
        if request.method == 'POST':
            # Extract POST Values sent from the client side.
            amount = request.form['amount']
            phone = request.form['phone']

            # Provide consumer_key and consumer_secret provided by safaricom
            consumer_key = "GTWADFxIpUfDoNikNGqq1C3023evM6UH"
            consumer_secret = "amFbAoUByPV2rM5A"

            # Authenticate Yourself using above credentials to Safaricom Services, and Bearer Token this is used by safaricom for security identification purposes - Your are given Access
            api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"  # AUTH URL
            # Provide your consumer_key and consumer_secret 
            response = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
            # Get response as Dictionary 
            data = response.json()
            # Retrieve the Provide Token
            # Token allows you to proceed with the transaction
            access_token = "Bearer" + ' ' + data['access_token']
            #  GETTING THE PASSWORD
            timestamp = datetime.datetime.today().strftime('%Y%m%d%H%M%S')  # Current Time
            passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'  # Passkey(Safaricom Provided)
            business_short_code = "174379"  # Test Paybile (Safaricom Provided)
            # Combine above 3 Strings to get data variable
            data = business_short_code + passkey + timestamp
            # Encode to Base64
            encoded = base64.b64encode(data.encode())
            password = encoded.decode()

            # BODY OR PAYLOAD
            payload = {
                "BusinessShortCode": "174379",
                "Password":password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": "1",  # use 1 when testing
                "PartyA": phone,  # change to your number
                "PartyB": "174379",
                "PhoneNumber": phone,
                "CallBackURL": "https://coding.co.ke/api/confirm.php",
                "AccountReference": "SokoGarden Online",
                "TransactionDesc": "Payments for Products"
            }

            # POPULAING THE HTTP HEADER, PROVIDE THE TOKEN ISSUED EARLIER
            headers = {
                "Authorization": access_token,
                "Content-Type": "application/json"
            }

            # Specify STK Push  Trigger URL
            url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"  
            # Create a POST Request to above url, providing headers, payload 
            # Below triggers an STK Push to the phone number indicated in the payload and the amount.
            response = requests.post(url, json=payload, headers=headers)
            print(response.text) 
            # Give a Response
            return jsonify({"message": "An MPESA Prompt has been sent to Your Phone, Please Check & Complete Payment"})
# Run app.
if __name__=='__main__':
    app.run(debug=True) 