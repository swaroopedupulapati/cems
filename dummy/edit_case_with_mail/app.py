"""from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify
from pymongo import MongoClient
import gridfs
from bson.objectid import ObjectId

app = Flask(__name__)

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
fs = gridfs.GridFS(my_db)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        case_number = request.form.get('case_number')
        labels = request.form.getlist('label[]')
        texts = request.form.getlist('data_text[]')
        files = request.files.getlist('data_file[]')

        # Prepare case details
        case_details = []
        for i in range(len(labels)):
            detail = {'label': labels[i], 'data': texts[i] if texts[i] else None}
            if files[i] and files[i].filename:
                file_id = fs.put(files[i], filename=files[i].filename)
                detail['file_id'] = str(file_id)
            case_details.append(detail)

        # Insert or update the case in MongoDB
        collection.update_one(
            {'case_number': case_number},
            {'$set': {'details': case_details}},
            upsert=True
        )
        return redirect(url_for('success'))

    return render_template('edit_case.html')


@app.route('/fetch_case/<case_number>', methods=['GET'])
def fetch_case(case_number):
    #Fetch case details by case number.
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


@app.route('/success')
def success():
    return "Case details have been successfully submitted or updated!"


@app.route('/downloadd_files/<file_id>')
def download(file_id):
    #Download file from GridFS using file_id.
    file_data = fs.get(ObjectId(file_id))
    return send_file(file_data, download_name=file_data.filename, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
"""


"""
from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify
from pymongo import MongoClient
import gridfs
from bson.objectid import ObjectId

app = Flask(__name__)

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
fs = gridfs.GridFS(my_db)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        case_number = request.form.get('case_number')
        labels = request.form.getlist('label[]')
        texts = request.form.getlist('data_text[]')
        files = request.files.getlist('data_file[]')

        # Prepare case details
        case_details = []
        for i in range(len(labels)):
            detail = {'label': labels[i], 'data': texts[i] if texts[i] else None}
            if files[i] and files[i].filename:
                file_id = fs.put(files[i], filename=files[i].filename)
                detail['file_id'] = str(file_id)
            case_details.append(detail)

        # Insert or update the case in MongoDB
        collection.update_one(
            {'case_number': case_number},
            {'$set': {'details': case_details}},
            upsert=True
        )
        return redirect(url_for('success'))

    return render_template('edit_case.html')


@app.route('/fetch_case/<case_number>', methods=['GET'])
def fetch_case(case_number):
    #Fetch case details by case number.
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


@app.route('/success')
def success():
    return "Case details have been successfully submitted or updated!"


@app.route('/downloadd_files/<file_id>')
def download(file_id):
    #Download file from GridFS using file_id.
    file_data = fs.get(ObjectId(file_id))
    return send_file(file_data, download_name=file_data.filename, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
"""


from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify, Response
from pymongo import MongoClient
import gridfs
from bson.objectid import ObjectId

from io import BytesIO
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from pymongo import MongoClient
import gridfs
from bson import ObjectId
import mimetypes
import fitz  # PyMuPDF


app = Flask(__name__)

# MongoDB Configuration
"""host = "ocdb.app"
port = 5050
database = "db_43589fyv5"
username = "user_43589fyv5"
password = "p43589fyv5"

connection_string = f"mongodb://{username}:{password}@{host}:{port}/{database}"
my_client = MongoClient(connection_string)
my_db = my_client[database]
collection = my_db['cases']
fs = gridfs.GridFS(my_db)
"""
mydb = "mongodb+srv://i_am_swaroop:swaroop%402004@theswaroopdb.ofpw0zm.mongodb.net/?retryWrites=true&w=majority&appName=theswaroopdb"
client = MongoClient(mydb)
my_db = client["swaroopdb"]
collection = my_db['cases']
fs = gridfs.GridFS(my_db)  # Initialize GridFS
higher_credentials = my_db["higher_credentials"]
lower_credentials=my_db["lower_credentials"]
ledger=my_db["ledger"]

# Email Configuration
SENDER_EMAIL = "swaroopqis@gmail.com"
SENDER_PASSWORD =  "qihb sgty ysew ikes"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587




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



@app.route('/edit_case', methods=['GET', 'POST'])
def edit_case():
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

    return render_template('edit_case.html')


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


if __name__ == '__main__':
    app.run(debug=True)
