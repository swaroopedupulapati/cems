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


@app.route('/downloadd/<file_id>')
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


@app.route('/downloadd/<file_id>')
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


@app.route('/edit_case', methods=['GET', 'POST'])
def edit_case():
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
        return "Case details have been successfully submitted or updated!"

    return render_template('edit_case.html')


@app.route('/fetch_case/<case_number>', methods=['GET'])
def fetch_case(case_number):
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

@app.route('/downloadd/<file_id>')
def downloadd(file_id):
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
