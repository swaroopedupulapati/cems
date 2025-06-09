from flask import Flask, render_template, request, redirect, url_for, send_file
from pymongo import MongoClient
import gridfs
from bson.objectid import ObjectId

app = Flask(__name__)

# """# MongoDB Configuration
# client = MongoClient('your_mongodb_connection_string')
# db = client['case_management']
# collection = db['cases']
# fs = gridfs.GridFS(db) """ # Initialize GridFS

host = "ocdb.app"
port = 5050
database = "db_43589fyv5" # your database
username = "user_43589fyv5" # your username
password = "p43589fyv5" # your password
 
connection_string = f"mongodb://{username}:{password}@{host}:{port}/{database}"
my_client = MongoClient(connection_string)
my_db = my_client[database]
collection = my_db['cases']
fs = gridfs.GridFS(my_db)  # Initialize GridFS




@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get case number
        case_number = request.form.get('case_number')
        
        # Get labels and data
        labels = request.form.getlist('label[]')
        texts = request.form.getlist('data_text[]')
        files = request.files.getlist('data_file[]')

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
        return redirect(url_for('success'))
    
    return render_template('index.html')

@app.route('/success')
def success():
    return "Case details and files have been successfully submitted!"

@app.route('/download/<file_id>')
def download(file_id):
    #Download file from GridFS using file_id.
    file_data = fs.get(ObjectId(file_id))
    return send_file(file_data, download_name=file_data.filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
