from flask import Flask, request, render_template, redirect, url_for, jsonify, flash, send_file, Response,session
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
  # PyMuPDF for PDF processing
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import time
import random
from pytz import timezone 
from datetime import datetime


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for using sessions


# MongoDB Configuration
host = "ocdb.app"
"""port = 5050
database = "db_43589fyv5"
username = "user_43589fyv5"
password = "p43589fyv5"

connection_string = f"mongodb://{username}:{password}@{host}:{port}/{database}"
my_client = MongoClient(connection_string)
my_db = my_client[database]"""


mydb = "db connection"
client = MongoClient(mydb)
my_db = client["swaroopdb"]
collection = my_db['cases']
fs = gridfs.GridFS(my_db)  # Initialize GridFS
higher_credentials = my_db["higher_credentials"]
lower_credentials=my_db["lower_credentials"]
ledger=my_db["ledger"]

# Email Configuration
SENDER_EMAIL = "mail id"
SENDER_PASSWORD =  "password or pass key"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587



default_user = {"id":"100","Name":"police","password":"police@1234",
                                         "Email":"policw@gmail.com","phone_no":"100","Address":"police station",
                                         "Qualification":"Ntg"
                                          # You should hash passwords in real apps!
}

# Check if collection is empty
if higher_credentials.count_documents({}) == 0:
    higher_credentials.insert_one(default_user)
    print("✅ Default login user inserted.")
else:
    print("ℹ️ Login collection already has users. No action taken.")

if lower_credentials.count_documents({}) == 0:
    lower_credentials.insert_one(default_user)
    print("✅ Default login user inserted.")
else:
    print("ℹ️ Login collection already has users. No action taken.")





# Function to generate OTP
def generate_otp():
    otp = random.randint(100000, 999999)  # Generates a 6-digit OTP
    print(otp)
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

@app.route('/generate_otp', methods=['POST'])
def generate_otp_route():
    if request.form.get('email'):
        email = request.form.get('email')
    elif request.form.get('user_id'):
        user_id = request.form.get('user_id')
        email = higher_credentials.find_one({"id": user_id})['Email']

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

# home
@app.route('/',methods=['GET', 'POST'])
def home():
    if request.method=='POST':
        login_type=request.form["login"]
        if login_type=="hlogin":
            return render_template('higher_login.html')
        elif login_type=="llogin":
            return render_template('lower_login.html')
    else:
        return render_template("about.html")
    return render_template('lower_login.html')

# higher home after login
@app.route('/higher_login',methods=['GET', 'POST'])
def higher_login():
    global higher_credentials
    id=request.form['id']
    global higher_id
    higher_id=id
    password=request.form['password']
    if higher_credentials.find_one({"id":id,"password":password}) :
        a=list(higher_credentials.find_one({"id":id,"password":password}))
        print(a)
        return redirect(f"/{id}/hio_home")
    else:
        return render_template("higher_login.html",msg="invalid credentials")

# lower home after login
@app.route('/lower_login',methods=['GET', 'POST'])
def lower_login():
    global lower_credentials
    id=request.form['id']
    global lower_id
    lower_id=id
    password=request.form['password']
    if lower_credentials.find_one({"id":id,"password":password}) :
        a=list(lower_credentials.find_one({"id":id,"password":password}))
        print(a)
        return redirect(f"/{id}/loo_home")
    else:
        return render_template("lower_login.html",msg="invalid credentials")


@app.route('/<id>/hio_home',methods=['GET',"POST"])
def hio_home(id):
    return render_template('higher_home.html',id=id)

@app.route('/<id>/loo_home',methods=['GET',"POST"])
def loo_home(id):
    return render_template('lower_home.html',id=id)

# for viewing higher profile
@app.route('/<id>/viewhipro',methods=['GET', 'POST'])
def viewhipro(id):
    data=dict(higher_credentials.find_one({"id":id}))
    return render_template("view_hip.html",profile=data)

# for viewing lower profile
@app.route('/<id>/viewlopro',methods=['GET', 'POST'])
def viewlopro(id):
    global lower_id
    data=dict(lower_credentials.find_one({"id":id}))
    return render_template("view_lop.html",id=id,profile=data)

# for registering higher offiecial
@app.route('/<id>/reghio',methods=['GET', 'POST'])
def reghio(id):
    if request.method == 'POST':
        global higher_credentials
        ID=request.form['id']
        Name=request.form['name']
        Password=f"{ID}@123"
        Email=request.form["email"]
        Phone=request.form["phone"]
        Address=request.form["address"]
        Qualification=request.form["qualification"]
        if higher_credentials.find_one({"id":ID})or lower_credentials.find_one({"id":ID}):
            return render_template("register_hio.html",id=id,msg=f"{ID} already exists")
        else:
            higher_credentials.insert_one({"id":ID,"Name":Name,"password":Password,
                                         "Email":Email,"phone_no":Phone,"Address":Address,
                                         "Qualification":Qualification
                                         })
            date = datetime.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d')
            time = datetime.now(timezone("Asia/Kolkata")).strftime('%H:%M')
            ledger.insert_one({"Date":f"{date}","Time":f"{time}","Data":f"{ID} registered as higher official"})
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
            return render_template("register_hio.html",id=id,msg=f"{ID} updated successfully")
    else:
        return render_template("register_hio.html",id=id)

# for registering lower official
@app.route('/<id>/regloo',methods=['GET', 'POST'])
def regloo(id):
    if request.method == 'POST':
        global lower_credentials
        ID=request.form['id']
        Name=request.form['name']
        Password=f"{ID}@123"
        Email=request.form["email"]
        Phone=request.form["phone"]
        Address=request.form["address"]
        Qualification=request.form["qualification"]
        if lower_credentials.find_one({"id":ID}) or higher_credentials.find_one({"id":ID}):
            return render_template("register_loo.html",id=id,msg=f"{ID} already exists")
        else:
            lower_credentials.insert_one({"id":ID,"Name":Name,"password":Password,
                                         "Email":Email,"phone_no":Phone,"Address":Address,
                                         "Qualification":Qualification
                                         })
            date = datetime.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d')
            time = datetime.now(timezone("Asia/Kolkata")).strftime('%H:%M')
            ledger.insert_one({"Date":f"{date}","Time":f"{time}","Data":f"{ID} registered as lower official"})
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
                head=MIMEText(f"Your successfully registerd for lower officials in \n Crime evidence Management system", 'plain')
                msg.attach(head)
                text_part = MIMEText(f"""\nyour credentials\n ID:{ID}\n Name:{Name}\n Password:{Password}\n Email:{Email}\n Phone:{Phone}\n Address:{Address}\n Qualification:{Qualification}""", 'plain')
                msg.attach(text_part)
                    # Send the email
                server.sendmail(SENDER_EMAIL, Email, msg.as_string())
                server.quit()
                print("Email sent successfully!")
            except Exception as e:
                print(f"Failed to send email: {e}")
            return render_template("register_loo.html",id=id,msg=f"{ID} updated successfully")
    else:
        return render_template("register_loo.html",id=id)

# for removing higher official
@app.route('/<id>/remhio',methods=['GET', 'POST'])
def remhio(id):
    if request.method == 'POST':
        eid=request.form['eid']
        reid=request.form['reid']
        if eid==reid and (higher_credentials.find_one({"id":eid})):
            higher_credentials.delete_one({"id":eid})
            date = datetime.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d')
            time = datetime.now(timezone("Asia/Kolkata")).strftime('%H:%M')
            ledger.insert_one({"Date":f"{date}","Time":f"{time}","Data":f"{eid} removed as higher official"})
            return render_template("remove_hio.html",id=id,msg=f"{eid} removed successfully")
        else:
            return render_template("remove_hio.html",id=id,msg="Invalid")
    else:
        return render_template("remove_hio.html",id=id)

# for removing lower official
@app.route('/<id>/remloo',methods=['GET', 'POST'])
def remloo(id):
    if request.method == 'POST':
        eid=request.form['eid']
        reid=request.form['reid']
        if eid==reid and (lower_credentials.find_one({"id":eid})):
            lower_credentials.delete_one({"id":eid})
            date = datetime.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d')
            time = datetime.now(timezone("Asia/Kolkata")).strftime('%H:%M')
            ledger.insert_one({"Date":f"{date}","Time":f"{time}","Data":f"{eid} removed as lower official"})
            return render_template("remove_loo.html",id=id,msg=f"{eid} removed successfully")
        else:
            return render_template("remove_loo.html",id=id,msg="Invalid")
    else:
        return render_template("remove_loo.html",id=id)

# for changing password for higher official
@app.route('/<id>/hio_changepasss',methods=['GET', 'POST'])
def hio_changepasss(id):
    global higher_id
    if request.method == 'POST':
        op=request.form['op']
        np=request.form['np']
        if higher_credentials.find_one({"id":id,"password":op}):
            higher_credentials.update_many({"id":id},{"$set":{"password":np}})
            return render_template("change_hio_pass.html",id=id,msg=f"password updated successfully")
        else:
            return render_template("change_hio_pass.html",id=id,msg=f"Invalid")
    else:
        return render_template("change_hio_pass.html",id=id)

# for changing password for lower official
@app.route('/<id>/loo_changepasss',methods=['GET', 'POST'])
def loo_changepasss(id):
    global lower_id
    if request.method == 'POST':
        op=request.form['op']
        np=request.form['np']
        if lower_credentials.find_one({"id":id,"password":op}):
            lower_credentials.update_many({"id":id},{"$set":{"password":np}})
            return render_template("change_loo_pass.html",id=id,msg=f"password updated successfully")
        else:
            return render_template("change_loo_pass.html",id=id)
    else:
        return render_template("change_loo_pass.html",id=id)

# for adding new case
@app.route('/<id>/add_case', methods=['GET', 'POST'])
def add_case(id):
    if request.method == 'POST':
        # Get case number
        case_number = request.form.get('case_number')
        
        # Get labels and data
        labels = request.form.getlist('label[]')
        texts = request.form.getlist('data_text[]')
        files = request.files.getlist('data_file[]')
        if case_number :
            if collection.find_one({"case_number":case_number}): 
                return render_template("add_case.html",id=id,msg="Case Number already exists")
            else:
                # Store case details
                case_details = []
                for i in range(len(labels)):
                    detail = {'label': labels[i], 'data': texts[i] if texts[i] else None}
                    
                    # Store file in GridFS if uploaded
                    if files[i] and files[i].filename:
                        file_id = fs.put(files[i], filename=files[i].filename)
                        detail['file_id'] = str(file_id)  # Store file ID in MongoDB
                    
                    case_details.append(detail)
                
                # Insert case data into MongoDB
                case_data = {
                    'case_number': case_number,
                    'details': case_details
                }
                collection.insert_one(case_data)
                date = datetime.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d')
                time = datetime.now(timezone("Asia/Kolkata")).strftime('%H:%M')
                ledger.insert_one({"Date":f"{date}","Time":f"{time}","Data":f"{case_number} added"} )
                return render_template("add_case.html",id=id,msg=f"case added successfully")
        else:
            return render_template("add_case.html",id=id,msg=f"Invalid")
    else:
        return render_template('add_case.html',id=id)


@app.route('/download/<file_id>')
def download(file_id):
    """Download file from GridFS using file_id."""
    file_data = fs.get(ObjectId(file_id))
    return send_file(file_data, download_name=file_data.filename, as_attachment=True)

# for viewing existing case
@app.route('/<id>/view', methods=['GET', 'POST'])
def view(id):
    case_data = None
    file_contents = []

    if request.method == 'POST':
        case_number = request.form.get('case_number')
        case_data = collection.find_one({'case_number': case_number})

        if case_data:
            case_details_with_files = []

            for detail in case_data['details']:
                file_info = None
                if 'file_id' in detail:
                    file_data = fs.get(ObjectId(detail['file_id']))
                    mime_type = mimetypes.guess_type(file_data.filename)[0]

                    if mime_type and mime_type.startswith('text'):
                        file_content = file_data.read().decode('utf-8')
                        file_info = {'type': 'text', 'label': detail['label'], 'content': file_content}
                    elif mime_type == 'application/pdf':
                        pdf_content = base64.b64encode(file_data.read()).decode('utf-8')
                        file_info = {'type': 'pdf', 'label': detail['label'], 'content': pdf_content}
                    elif mime_type and mime_type.startswith('image'):
                        image_data = base64.b64encode(file_data.read()).decode('utf-8')
                        file_info = {'type': 'image', 'label': detail['label'], 'content': f"data:{mime_type};base64,{image_data}"}
                    else:
                        binary_data = file_data.read()
                        file_info = {'type': 'binary', 'label': detail['label'], 'content': str(binary_data)}

                case_details_with_files.append({'detail': detail, 'file': file_info})

            file_contents = case_details_with_files
        else:
            return render_template("view_case.html",msg="not occur",id=id)
    return render_template('view_case.html', id=id,case_data=case_data, file_contents=file_contents)


@app.route('/download_pdf/<case_number>')
def download_pdf(case_number):
    case_data = collection.find_one({'case_number': case_number})
    if not case_data:
        flash('No case found with the given case number.', 'error')
        return redirect(url_for('view'))

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Title for the case
    title = Paragraph(f"<strong>Case Details for Case Number: {case_data['case_number']}</strong>", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))

    for detail in case_data['details']:
        # Add case details
        elements.append(Paragraph(f"<strong> {detail['label']}</strong>", styles['BodyText']))
        elements.append(Paragraph(f" {detail['data']}", styles['BodyText']))
        elements.append(Spacer(1, 12))

        # Handle file data
        if 'file_id' in detail:
            file_data = fs.get(ObjectId(detail['file_id']))
            mime_type = mimetypes.guess_type(file_data.filename)[0]

            if mime_type and mime_type.startswith('text'):
                # Include text file content
                try:
                    file_content = file_data.read().decode('utf-8')
                    elements.append(Paragraph(f"<strong>File Content (Text):</strong>", styles['BodyText']))
                    elements.append(Paragraph(file_content, styles['BodyText']))
                except UnicodeDecodeError:
                    elements.append(Paragraph(f"<strong>File Content (Text):</strong> Unable to decode text content", styles['BodyText']))
                elements.append(Spacer(1, 12))

            elif mime_type == 'application/pdf':
                # Handle PDF file content
                elements.append(Paragraph(f"<strong>File Content (PDF):</strong>", styles['BodyText']))

                # Convert PDF pages to images and add them to the PDF
                pdf_buffer = BytesIO(file_data.read())
                pdf_document = fitz.open(stream=pdf_buffer, filetype="pdf")
                for page_num in range(pdf_document.page_count):
                    page = pdf_document.load_page(page_num)
                    pix = page.get_pixmap()
                    img_data = BytesIO(pix.tobytes())  # Convert page to image
                    img = Image(img_data, width=400, height=300)
                    elements.append(img)
                    elements.append(Spacer(1, 12))
                
                elements.append(Spacer(1, 12))

            elif mime_type and mime_type.startswith('image'):
                # Embed image in the PDF
                img_data = BytesIO(file_data.read())
                img = Image(img_data, width=400, height=300)
                elements.append(img)
                elements.append(Spacer(1, 12))

            else:
                # Binary or unsupported file content
                binary_content = file_data.read().decode('latin1', errors='replace')
                elements.append(Paragraph(f"<strong>File Content (Binary):</strong>", styles['BodyText']))
                elements.append(Paragraph(binary_content[:500] + "...", styles['BodyText']))  # Limit binary content to the first 500 characters
                elements.append(Spacer(1, 12))

    # Build the PDF document
    doc.build(elements)
    buffer.seek(0)

    return send_file(
        buffer,
        download_name=f"case_{case_number}_details.pdf",
        as_attachment=True,
        mimetype='application/pdf'
    )


def create_case_pdf(case_data):
    """
    Generate a PDF for the given case data.
    :param case_data: Dictionary containing case details.
    :return: BytesIO object containing the generated PDF.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Title for the case
    title = Paragraph(f"<strong>Case Details for Case Number: {case_data['case_number']}</strong>", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))

    for detail in case_data['details']:
        # Add case details
        elements.append(Paragraph(f"<strong>{detail['label']}</strong>", styles['BodyText']))
        elements.append(Paragraph(f"{detail['data']}", styles['BodyText']))
        elements.append(Spacer(1, 12))

        # Handle file data
        if 'file_id' in detail:
            file_data = fs.get(ObjectId(detail['file_id']))
            mime_type = mimetypes.guess_type(file_data.filename)[0]

            if mime_type and mime_type.startswith('text'):
                # Include text file content
                try:
                    file_content = file_data.read().decode('utf-8')
                    elements.append(Paragraph(f"<strong></strong>", styles['BodyText']))
                    elements.append(Paragraph(file_content, styles['BodyText']))
                except UnicodeDecodeError:
                    elements.append(Paragraph(f"<strong></strong> Unable to decode text content", styles['BodyText']))
                elements.append(Spacer(1, 12))

            elif mime_type == 'application/pdf':
                # Handle PDF file content
                elements.append(Paragraph(f"<strong></strong>", styles['BodyText']))

                # Convert PDF pages to images and add them to the PDF
                pdf_buffer = BytesIO(file_data.read())
                pdf_document = fitz.open(stream=pdf_buffer, filetype="pdf")
                for page_num in range(pdf_document.page_count):
                    page = pdf_document.load_page(page_num)
                    pix = page.get_pixmap()
                    img_data = BytesIO(pix.tobytes())  # Convert page to image
                    img = Image(img_data, width=400, height=300)
                    elements.append(img)
                    elements.append(Spacer(1, 12))
                
                elements.append(Spacer(1, 12))

            elif mime_type and mime_type.startswith('image'):
                # Embed image in the PDF
                img_data = BytesIO(file_data.read())
                img = Image(img_data, width=400, height=300)
                elements.append(img)
                elements.append(Spacer(1, 12))

    # Build the PDF document
    doc.build(elements)
    buffer.seek(0)
    return buffer


def send_email_with_attachment(recipient_email, subject, body, pdf1,pdf2, pr_name,up_name):
    """
    Send an email with the provided PDF as an attachment using Gmail.
    :param recipient_email: Email address of the recipient.
    :param subject: Email subject.
    :param body: Email body text.
    :param pdf1: BytesIO object containing the PDF.
    :param pr_name: Name of the PDF attachment.

    """

    a=list(higher_credentials.find())
    emails = [item['Email'] for item in a]
    print(emails)
    for email in emails:
        try:
            # Set up the SMTP server
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)

            # Create the email
            msg = MIMEMultipart()
            msg['From'] = SENDER_EMAIL
            msg['To'] = email   #recipient_email
            msg['Subject'] = subject

            # Attach the email body
            msg.attach(MIMEText(body, 'plain'))
            text_part = MIMEText(f"this mail contains the previous and updated case details about the case no {body}\n\n", 'plain')
            msg.attach(text_part)
        
            # Attach the PDF
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(pdf1.getvalue())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{pr_name}"')
            msg.attach(part)

            # Attach the PDF
            part2 = MIMEBase('application', 'octet-stream')
            part2.set_payload(pdf2.getvalue())
            encoders.encode_base64(part2)
            part2.add_header('Content-Disposition', f'attachment; filename="{up_name}"')
            msg.attach(part2)

            # Send the email
            server.sendmail(SENDER_EMAIL, recipient_email, msg.as_string())
            server.quit()
            print("Email sent successfully!")
        except Exception as e:
            print(f"Failed to send email: {e}")





def create_case_pdf(case_data):
    """
    Generate a PDF for the given case data.
    :param case_data: Dictionary containing case details.
    :return: BytesIO object containing the generated PDF.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Title for the case
    title = Paragraph(f"<strong>Case Details for Case Number: {case_data['case_number']}</strong>", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))

    for detail in case_data['details']:
        # Add case details
        elements.append(Paragraph(f"<strong>{detail['label']}</strong>", styles['BodyText']))
        elements.append(Paragraph(f"{detail['data']}", styles['BodyText']))
        elements.append(Spacer(1, 12))

        # Handle file data
        if 'file_id' in detail:
            file_data = fs.get(ObjectId(detail['file_id']))
            mime_type = mimetypes.guess_type(file_data.filename)[0]

            if mime_type and mime_type.startswith('text'):
                # Include text file content
                try:
                    file_content = file_data.read().decode('utf-8')
                    elements.append(Paragraph(f"<strong></strong>", styles['BodyText']))
                    elements.append(Paragraph(file_content, styles['BodyText']))
                except UnicodeDecodeError:
                    elements.append(Paragraph(f"<strong></strong> Unable to decode text content", styles['BodyText']))
                elements.append(Spacer(1, 12))

            elif mime_type == 'application/pdf':
                # Handle PDF file content
                elements.append(Paragraph(f"<strong></strong>", styles['BodyText']))

                # Convert PDF pages to images and add them to the PDF
                pdf_buffer = BytesIO(file_data.read())
                pdf_document = fitz.open(stream=pdf_buffer, filetype="pdf")
                for page_num in range(pdf_document.page_count):
                    page = pdf_document.load_page(page_num)
                    pix = page.get_pixmap()
                    img_data = BytesIO(pix.tobytes())  # Convert page to image
                    img = Image(img_data, width=400, height=300)
                    elements.append(img)
                    elements.append(Spacer(1, 12))
                
                elements.append(Spacer(1, 12))

            elif mime_type and mime_type.startswith('image'):
                # Embed image in the PDF
                img_data = BytesIO(file_data.read())
                img = Image(img_data, width=400, height=300)
                elements.append(img)
                elements.append(Spacer(1, 12))

    # Build the PDF document
    doc.build(elements)
    buffer.seek(0)
    return buffer

def send_email_with_attachment(recipient_email, subject, body, pdf1,pdf2, pr_name,up_name):
    """
    Send an email with the provided PDF as an attachment using Gmail.
    :param recipient_email: Email address of the recipient.
    :param subject: Email subject.
    :param body: Email body text.
    :param pdf1: BytesIO object containing the PDF.
    :param pr_name: Name of the PDF attachment.
    """
    try:
        # Set up the SMTP server
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)

        # Create the email
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = recipient_email
        msg['Subject'] = subject

        # Attach the email body
        msg.attach(MIMEText(body, 'plain'))
        text_part = MIMEText(f"this mail contains the previous and updated case details about the case no {body}\n\n", 'plain')
        msg.attach(text_part)
    
        # Attach the PDF
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(pdf1.getvalue())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="{pr_name}"')
        msg.attach(part)

        # Attach the PDF
        part2 = MIMEBase('application', 'octet-stream')
        part2.set_payload(pdf2.getvalue())
        encoders.encode_base64(part2)
        part2.add_header('Content-Disposition', f'attachment; filename="{up_name}"')
        msg.attach(part2)

        # Send the email
        server.sendmail(SENDER_EMAIL, recipient_email, msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")



@app.route('/<id>/edit_case', methods=['GET', 'POST'])
def edit_case(id):
    if request.method == 'POST':
        case_number = request.form.get('case_number')
        labels = request.form.getlist('label[]')
        texts = request.form.getlist('data_text[]')
        files = request.files.getlist('data_file[]')

        # Fetch the existing case details
        existing_case = collection.find_one({'case_number': case_number})
        existing_details = existing_case['details'] if existing_case else []

        # Create a dictionary of existing file mappings for quick lookup
        existing_files = {detail['label']: detail.get('file_id') for detail in existing_details}

        # Prepare new case details
        case_details = []
        for i in range(len(labels)):
            label = labels[i]
            text = texts[i] if texts[i] else None
            file = files[i]

            detail = {'label': label, 'data': text}

            # Check if a new file is uploaded
            if file and file.filename:
                # Upload new file to GridFS
                file_id = fs.put(file, filename=file.filename)
                detail['file_id'] = str(file_id)
            else:
                # Retain existing file ID if no new file is uploaded
                if label in existing_files:
                    detail['file_id'] = existing_files[label]

            case_details.append(detail)
        recipient_email = "swaroopedupulapati1@gmail.com"
        casedata = collection.find_one({'case_number': case_number})
        pdf1 = create_case_pdf(casedata)


        # Update the case in MongoDB
        collection.update_one(
            {'case_number': case_number},
            {'$set': {'details': case_details}},
            upsert=True
        )
        case_data = collection.find_one({'case_number': case_number})
        pdf2=create_case_pdf(case_data)


        
        # Send Email
        subject = f"Case Details for Case Number {case_number}"
        body = f"{case_number}."
        pr_name = f"case_{case_number}_details.pdf"
        up_name= f"case_{case_number}_updated_details.pdf"
        send_email_with_attachment(recipient_email, subject, body, pdf1,pdf2, pr_name,up_name)


        return "Case details have been successfully updated!"

    return render_template('edit_case.html',id=id)


@app.route('/fetch_case_details/<case_number>', methods=['GET'])
def fetch_case_details(case_number):
    """Fetch case details by case number."""
    case = collection.find_one({'case_number': case_number})
    if case:
        # Convert ObjectId fields to strings
        case['_id'] = str(case['_id'])
        for detail in case['details']:
            if 'file_id' in detail:
                detail['file_id'] = str(detail['file_id'])
                file = fs.get(ObjectId(detail['file_id']))
                detail['filename'] = file.filename
        return jsonify(case)
    return jsonify({'error': 'Case not found'}), 404

@app.route('/downloadd_files/<file_id>')
def downloadd_files(file_id):
    """Download or render files from GridFS using file_id."""
    file_data = fs.get(ObjectId(file_id))
    file_type = file_data.filename.split('.')[-1].lower()
    content_type = {
        'pdf': 'application/pdf',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'gif': 'image/gif',
        'mp4': 'video/mp4',
        'webm': 'video/webm',
        'mp3': 'audio/mpeg',
        'wav': 'audio/wav',
        'txt': 'text/plain',
        'csv': 'text/csv',
    }.get(file_type, 'application/octet-stream')

    return Response(file_data.read(), content_type=content_type)



# for sending email for removing case
def send_email(recipient_email, subject, body, pdf1, pr_name,):
    
    try:
        # Set up the SMTP server
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)

        # Create the email
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = recipient_email
        msg['Subject'] = subject

        # Attach the email body
        msg.attach(MIMEText(body, 'plain'))
        text_part = MIMEText(f"this mail contains the details about the case no {body} has beeen removed\n\n", 'plain')
        msg.attach(text_part)
    
        # Attach the PDF
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(pdf1.getvalue())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="{pr_name}"')
        msg.attach(part)

        # Send the email
        server.sendmail(SENDER_EMAIL, recipient_email, msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

# for removing existing case
@app.route('/<id>/removecase',methods=['GET', 'POST'])
def removecase(id):
    if request.method == 'POST':
        case_no=request.form['case_no']
        rcase_no=request.form['rcase_no']
        if case_no== rcase_no and (collection.find_one({'case_number': case_no})):
            recipient_email = "swaroopedupulapati1@gmail.com"
            casedata = collection.find_one({'case_number': case_no})
            pdf1 = create_case_pdf(casedata)
            # Send Email
            subject = f"Case Details for Case Number {case_no}"
            body = f"{case_no}."
            pr_name = f"case_{case_no}_details.pdf"
            send_email(recipient_email, subject, body, pdf1, pr_name)

            collection.delete_one({'case_number': case_no})
            date = datetime.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d')
            time = datetime.now(timezone("Asia/Kolkata")).strftime('%H:%M')
            ledger.insert_one({"Date":f"{date}","Time":f"{time}","Data":f"{case_no} has been removed by {id}"} )
            return render_template("remove_case.html",msg=f"{case_no} has been removed successfully")
        else:
            return render_template("remove_case.html",msg=f"{case_no} has been removed successfully")
    else:
        return render_template("remove_case.html",id=id)



# for viewing ledger
@app.route('/<id>/viewledger',methods=['GET', 'POST'])
def viewledger(id):
    data=list(ledger.find())
    return render_template("ledger.html",id=id,ledger=data)




if __name__ == '__main__':
    app.run(debug=True)