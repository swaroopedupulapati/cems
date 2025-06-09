from flask import Flask, render_template, request, flash, send_file, url_for
from pymongo import MongoClient
import gridfs
from bson.objectid import ObjectId
import mimetypes
import base64

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # For flash messages

# MongoDB Configuration
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

@app.route('/view', methods=['GET', 'POST'])
def view():
    case_data = None
    file_contents = []
    
    if request.method == 'POST':
        case_number = request.form.get('case_number')
        case_data = collection.find_one({'case_number': case_number})
        
        if case_data:
            # Prepare the case details and file contents together
            case_details_with_files = []
            
            for detail in case_data['details']:
                file_info = None
                if 'file_id' in detail:
                    file_data = fs.get(ObjectId(detail['file_id']))
                    mime_type = mimetypes.guess_type(file_data.filename)[0]
                    
                    if mime_type and mime_type.startswith('text'):  # Text files
                        file_content = file_data.read().decode('utf-8')
                        file_info = {'type': 'text', 'label': detail['label'], 'content': file_content}
                    elif mime_type == 'application/pdf':  # PDF files
                        pdf_url = url_for('download', file_id=detail['file_id'])
                        file_info = {'type': 'pdf', 'label': detail['label'], 'url': pdf_url}
                    elif mime_type and mime_type.startswith('image'):  # Images
                        image_data = base64.b64encode(file_data.read()).decode('utf-8')
                        file_info = {'type': 'image', 'label': detail['label'], 'content': f"data:{mime_type};base64,{image_data}"}
                    else:  # Unsupported/binary files
                        download_url = url_for('download', file_id=detail['file_id'])
                        file_info = {'type': 'binary', 'label': detail['label'], 'url': download_url}
                
                case_details_with_files.append({'detail': detail, 'file': file_info})
            
            file_contents = case_details_with_files
        else:
            flash('No case found with the given case number.', 'error')
    
    return render_template('view_all.html', case_data=case_data, file_contents=file_contents)

@app.route('/download/<file_id>')
def download(file_id):
    """Download file from GridFS using file_id."""
    file_data = fs.get(ObjectId(file_id))
    return send_file(file_data, download_name=file_data.filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)

