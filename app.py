from flask import Flask, render_template, request
import hashlib
from difflib import SequenceMatcher

app = Flask(__name__)

def hash_file(file_path):
    # Use hashlib to store the hash of a file
    h = hashlib.sha1()

    with open(file_path, "rb") as file:
        # Read the file in small chunks because we cannot read large files at once
        chunk = 0
        while chunk != b'':
            chunk = file.read(1024)
            h.update(chunk)

    # hexdigest() returns the hash in hexadecimal format
    return h.hexdigest()

def compare_content(file1_path, file2_path):
    with open(file1_path, "r", encoding="utf-8", errors="ignore") as file1, open(file2_path, "r", encoding="utf-8", errors="ignore") as file2:
        content1 = file1.read()
        content2 = file2.read()
        matcher = SequenceMatcher(None, content1, content2)
        return matcher.quick_ratio()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compare', methods=['POST'])
def compare():
    # Check if the POST request has the file part
    if 'file1' not in request.files or 'file2' not in request.files:
        return "Please provide two files for comparison."

    file1 = request.files['file1']
    file2 = request.files['file2']

    # Save the uploaded files to the server temporarily
    file1_path = "temp_file1"
    file2_path = "temp_file2"
    file1.save(file1_path)
    file2.save(file2_path)

    # Hash the files
    hash1 = hash_file(file1_path)
    hash2 = hash_file(file2_path)

    # Compare the hashes
    hash_result = "These files are identical" if hash1 == hash2 else "These files are not identical"

    # Compare the content
    content_similarity = compare_content(file1_path, file2_path)
    content_result = f"Content similarity: {content_similarity:.2%}"

    # Delete temporary files
    import os
    os.remove(file1_path)
    os.remove(file2_path)

    # Render the result template with the comparison results
    return render_template('results.html', hash_result=hash_result, content_result=content_result)

if __name__ == '__main__':
    app.run(debug=True)
