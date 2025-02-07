import json
from docx import Document
from LLM import LLM_Call
from flask import Flask, request, render_template, jsonify, send_file, session
import os
import io
from unzip import extract_zip
from os import walk
import shutil

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Required to use sessions

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load allowed extensions from JSON file
with open(os.path.join('extensions', 'allowed_extensions.json'), 'r') as file:
    allowed_extensions = json.load(file)['extensions']


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    files = request.files.getlist('file[]')
    responses = []
    most_recent_file = None
    most_recent_folder = None

    for file in files:
        if file:
            filename = file.filename.lower()

            # Check if the file type is allowed
            if filename.endswith(tuple(allowed_extensions)):
                
                # Handle .zip files separately
                if filename.endswith('.zip'):
                    # Save the zip file temporarily
                    zip_path = os.path.join(UPLOAD_FOLDER, file.filename)
                    file.save(zip_path)

                    # Extract the zip file contents
                    try:
                        extract_zip(zip_path, UPLOAD_FOLDER)
                        responses.append(f"Extracted: {file.filename}")
                        os.remove(zip_path)  # Remove the zip file after extraction
                        folder_name = os.path.splitext(file.filename)[0]
                        most_recent_folder =  folder_name  # Store only the folder name
                    except Exception as e:
                        responses.append(f"Failed to extract {file.filename}: {str(e)}")
                else:
                    # Handle regular allowed files
                    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
                    file.save(file_path)
                    responses.append(f"Uploaded: {file.filename}")
                    most_recent_file = file.filename  # Store the file name

            else:
                # If the file type is not allowed
                responses.append(f"Rejected: {file.filename} (Disallowed file type)")

    # Store the most recent file and folder in the session
    if most_recent_file:
        session['most_recent_file'] = most_recent_file
    if most_recent_folder:
        session['most_recent_folder'] = most_recent_folder

    return {'responses': responses}



@app.route('/generate-document', methods=['POST'])
def generate_document():
    
    # Retrieve the most recent file and folder from the session
    most_recent_file = session.get('most_recent_file')
    most_recent_folder = session.get('most_recent_folder')
    print(f"Most recent file: {most_recent_file}")
    print(f"Most recent folder: {most_recent_folder}")
    
    if not most_recent_file and not most_recent_folder:
        print("Error: No file or folder found in session.")
        return jsonify({'error': 'No file or folder found to generate document.'}), 400

    # Create a new Word document
    doc = Document()
    doc.add_heading(f"Functional Code Document: {most_recent_file or most_recent_folder}", level=1)

    # If there's a folder, set base_path to the folder path
    if most_recent_folder:
        base_path = os.path.join(UPLOAD_FOLDER, most_recent_folder)
    else:
        base_path = os.path.join(UPLOAD_FOLDER, most_recent_file)

    # Debugging: Log the path being processed
    print(f"Processing path: {base_path}")
    
    processed_files = 0  # Counter for valid processed files

    try:
        # If it's a directory (folder), iterate through files
        if os.path.isdir(base_path):  # It's a folder
            print(f"Processing extracted folder: {base_path}")
            for dirpath, _, filenames in os.walk(base_path):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)

                    # Check if the file extension is allowed
                    if filename.lower().endswith(tuple(allowed_extensions)):
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                                file_content = file.read()
                                print(f"Successfully read file: {file_path}")
                                print(f"Content:\n{file_content[:100]}...")  # First 100 characters for brevity

                                #LLM Call (Commented out for now)
                                response = LLM_Call(file_content)
                                print(f"LLM Response for {filename}: {response}")

                                # Add content to the document
                                doc.add_heading(f"File: {filename}", level=2)
                                doc.add_paragraph(f"Original Content:\n{response}\n")
                                # doc.add_paragraph(f"LLM Response:\n{response}\n")  # Uncomment when using LLM
                                processed_files += 1
                        except Exception as e:
                            print(f"Error reading file {filename}: {e}")
                    else:
                        print(f"Skipped file {filename} (disallowed extension)")
        else:  # It's a single file
            if most_recent_file.lower().endswith(tuple(allowed_extensions)):
                try:
                    with open(base_path, 'r', encoding='utf-8', errors='ignore') as file:
                        file_content = file.read()
                        print(f"Successfully read file: {base_path}")
                        print(f"Content:\n{file_content[:100]}...")  # First 100 characters for brevity

                        # LLM Call (Commented out for now)
                        # response = LLM_Call(file_content)
                        # print(f"LLM Response for {most_recent_file}: {response}")

                        # Add content to the document
                        doc.add_heading(f"File: {most_recent_file}", level=2)
                        doc.add_paragraph(f"Original Content:\n{file_content}\n")
                        # doc.add_paragraph(f"LLM Response:\n{response}\n")  # Uncomment when using LLM
                        processed_files += 1
                except Exception as e:
                    print(f"Error reading file {most_recent_file}: {e}")
            else:
                return jsonify({'error': 'Disallowed file type.'}), 400

        # If no files were processed
        if processed_files == 0:
            return jsonify({'error': 'No valid files found to process.'}), 400

        # Save the .docx file to an in-memory stream
        doc_output = io.BytesIO()
        doc.save(doc_output)
        doc_output.seek(0)

        # Delete the folder or file after processing
        try:
            if os.path.isdir(base_path):  # If it's a folder, delete recursively
                shutil.rmtree(base_path)  # Deletes the folder and all its contents
            else:  # Single file
                os.remove(base_path)
            print(f"{most_recent_file or most_recent_folder} and its contents have been deleted from the uploads folder.")
        except Exception as e:
            print(f"Error deleting {base_path}: {e}")

        # Send the .docx file as a downloadable attachment
        return send_file(
            doc_output,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            as_attachment=True,
            download_name=f'functional_document_{most_recent_file or most_recent_folder}.docx'
        )

    except Exception as e:
        print(f"Unexpected error during document generation: {e}")
        return jsonify({'error': 'An unexpected error occurred during document generation.'}), 500


@app.route('/cancel-selection', methods=['POST'])
def cancel_selection():
    try:
        # Delete all files in the uploads folder
        for filename in os.listdir(UPLOAD_FOLDER):
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)

        return jsonify({'message': 'All files have been deleted from the uploads folder.'}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to delete files: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(host ='0.0.0.0', debug = False)
