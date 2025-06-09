from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import random
from pymongo import MongoClient
import gridfs
from bson.objectid import ObjectId
import mimetypes
import base64
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
import fitz  # PyMuPDF
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for using sessions





# MongoDB Configuration
host = "ocdb.app"
port = 5050
database = "db_43589fyv5"
username = "user_43589fyv5"
password = "p43589fyv5"

connection_string = f"mongodb://{username}:{password}@{host}:{port}/{database}"
my_client = MongoClient(connection_string)
my_db = my_client[database]
collection = my_db['cases']
fs = gridfs.GridFS(my_db)  # Initialize GridFS
higher_credentials = my_db["higher_credentials"]
lower_credentials=my_db["lower_credentials"]
# Email Configuration
SENDER_EMAIL = "swaroopqis@gmail.com"
SENDER_PASSWORD =  "qihb sgty ysew ikes" # Replace with your Gmail password (use App Password if 2FA enabled)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Function to generate OTP
def generate_otp():
    otp = random.randint(100000, 999999)  # Generates a 6-digit OTP
    return otp

# Function to send OTP email
def send_otp_email(recipient_email, otp):
    try:
        # Set up the MIME message
        message = MIMEMultipart()
        message['From'] = SENDER_EMAIL
        message['To'] = recipient_email
        message['Subject'] = 'Your OTP Code'
        
        body = f'Your OTP is: {otp}'
        message.attach(MIMEText(body, 'plain'))
        
        # Connect to the Gmail SMTP server
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, recipient_email, message.as_string())
            print("OTP sent successfully")
    except Exception as e:
        print(f"Error sending OTP email: {e}")

@app.route('/', methods=['GET'])
def otp_page():
    return render_template('otp_page.html')

@app.route('/generate_otp', methods=['POST'])
def generate_otp_route():
    email = request.form.get('email')

    if email:
        # Generate OTP and store it in the session
        otp = generate_otp()
        session['otp'] = otp
        session['otp_time'] = time.time()

        # Send OTP to the provided email
        send_otp_email(email, otp)

        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'error', 'message': 'Email is required'})

@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    user_otp = request.form.get('otp')

    if 'otp' in session:
        stored_otp = session['otp']
        otp_time = session['otp_time']

        # Check if OTP is still valid (5-minute validity)
        if time.time() - otp_time < 300:  # 300 seconds = 5 minutes
            if int(user_otp) == stored_otp:  # Check if OTP matches
                return jsonify({'status': 'success', 'message': 'OTP Verified. You can now submit the form.'})
            else:
                return jsonify({'status': 'error', 'message': 'Invalid OTP. Please try again.'})
        else:
            return jsonify({'status': 'error', 'message': 'OTP expired. Please generate a new one.'})

    return jsonify({'status': 'error', 'message': 'OTP not generated yet.'})

@app.route('/submit_form', methods=['POST'])
def submit_form():
    # Get user input
    name = request.form['name']
    email = request.form['email']

    # You can now process the form data, for example, save it to a database, etc.
    # After submission, redirect to a different page.
    return redirect(url_for('success'))

@app.route('/success', methods=['GET'])
def success():
    return "Form submitted successfully! Welcome to the next page."


# for registering higher offiecial
@app.route('/reghio',methods=['GET', 'POST'])
def reghio():
    if request.method == 'POST':
        global higher_credentials
        ID=request.form['id']
        Name=request.form['name']
        Password=f"{ID}@123"
        Email=request.form["email"]
        Phone=request.form["phone"]
        Address=request.form["address"]
        Qualification=request.form["qualification"]
        if higher_credentials.find_one({"id":ID}):
            return render_template("otp_page.html",msg=f"{ID} already exists")
        else:
            higher_credentials.insert_one({"id":ID,"Name":Name,"password":Password,
                                         "Email":Email,"phone_no":Phone,"Address":Address,
                                         "Qualification":Qualification
                                         })
            try:
                # Set up the SMTP server
                server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
                server.starttls()
                server.login(SENDER_EMAIL, SENDER_PASSWORD)
                    # Create the email
                msg = MIMEMultipart()
                msg['From'] = SENDER_EMAIL
                msg['To'] = Email
                msg['Subject'] = "registration"
                    # Attach the email body
                head=MIMEText(f"Your successfully registerd for higher official in \n Crime evidence Management system", 'plain')
                msg.attach(head)
                text_part = MIMEText(f"""\nyour credentials\n ID:{ID}\n  Name:{Name}\n Password:{Password}\n Email:{Email}\n Phone:{Phone}\n Address:{Address}\nQualification:{Qualification}""", 'plain')
                msg.attach(text_part)
                    # Send the email
                server.sendmail(SENDER_EMAIL, Email, msg.as_string())
                server.quit()
                print("Email sent successfully!")
            except Exception as e:
                print(f"Failed to send email: {e}")
            return render_template("otp_page.html",msg=f"{ID} updated successfully")
    else:
        return render_template("otp_page.html")




if __name__ == '__main__':
    app.run(debug=True)
