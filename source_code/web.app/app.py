from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import base64
import os
from flask_cors import CORS
from flask import Flask, request, jsonify

app = Flask(__name__)


app = Flask(__name__, template_folder='', static_folder='static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost/postgres'
app.secret_key = 'mysecretkey'
db = SQLAlchemy(app)

# Enable CORS for all routes
CORS(app)

# --------------------------------------------------------------------------------------------------

# Define the model for the face_recognition table
class FaceRecognition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.TIMESTAMP)
    name = db.Column(db.String(255))
    image_data = db.Column(db.LargeBinary)
    __tablename__ = 'face_recognition1'  # Change this line to the correct table name


# Define the model for the users table
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    last_login = db.Column(db.TIMESTAMP, default=datetime.utcnow)

    # Specify the custom table name "users"
    __tablename__ = "users"

# --------------------------------------------------------------------------------------------------



# ... (existing code above)

# Route to get the list of face records
@app.route('/')
def list():
    # Check if user is logged in
    if 'logged_in' not in session or not session['logged_in']:
        return jsonify(message="Unauthorized"), 401  # Unauthorized status code

    page = request.args.get('page', 1, type=int)
    per_page = 7  # Number of records per page

    records = FaceRecognition.query.order_by(FaceRecognition.time.desc()).paginate(page=page, per_page=per_page)

    # Convert image data to Base64 and build the JSON response
    records_with_images = []
    for record in records.items:
        image_data = record.image_data
        image_base64 = base64.b64encode(image_data).decode("utf-8")
        record_with_image = {
            'id': record.id,
            'time': record.time.strftime("%Y-%m-%d %H:%M:%S"),
            'name': record.name,
            'image_data': f"data:image/jpeg;base64,{image_base64}"
        }
        records_with_images.append(record_with_image)

    return jsonify(records=records_with_images, pagination=records.page), 200  # OK status code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)

# --------------------------------------------------------------------------------------------------

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username and password match in the database
        user = User.query.filter_by(username=username, password=password).first()

        if user:
            # Set the logged_in and admin_user session variables
            session['logged_in'] = True
            session['admin_user'] = (user.username == 'admin')

            # Update the last login time for the user
            user.last_login = datetime.utcnow()
            db.session.commit()

            return jsonify(message="Login successful"), 200  # OK status code
        else:
            return jsonify(message="Invalid username or password"), 401  # Unauthorized status code

    # Return an error response if the request method is not POST
    return jsonify(message="Method not allowed"), 405  # Method Not Allowed status code

# --------------------------------------------------------------------------------------------------

# Log out route
@app.route('/logout', methods=['POST'])
def logout():
    # Clear the session data
    session.clear()
    return jsonify(message='Logout successful'), 200  # OK status code

# --------------------------------------------------------------------------------------------------

# Route to edit the name of the detected face file
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_name(id):
    # Check if the user is logged in
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))

    record = FaceRecognition.query.get(id)
    if not record:
        return "Record not found", 404

    # Check if the user is an admin or a regular user
    admin_user = session.get('admin_user', False)

    if request.method == 'POST':
        action = request.form['action']

        if action == 'delete' and admin_user:
            # Delete the detected face record from the database
            db.session.delete(record)
            db.session.commit()

            # Delete the corresponding image file from the folder
            folder_path = 'images1/' + record.name
            image_filename = f"{record.name}-{record.time.strftime('%Y-%m-%d_%H-%M-%S')}.jpg"
            image_path = os.path.join(folder_path, image_filename)
            if os.path.exists(image_path):
                os.remove(image_path)

            flash('Record deleted successfully', 'success')
            return redirect(url_for('list'))

        elif action == 'edit':
            # Update the name of the detected face file in the database
            new_name = request.form['new_name']
            record.name = new_name
            db.session.commit()

            flash('Name updated successfully', 'success')
            return redirect(url_for('list'))

    return render_template('edit_name.html', record=record)


# --------------------------------------------------------------------------------------------------

# Route to delete the detected face record from the database
@app.route('/delete/<int:id>', methods=['POST'])
def delete_record(id):
    # Check if the user is logged in and is an admin user
    if not session.get('logged_in') or not session.get('admin_user'):
        return redirect(url_for('login'))

    record = FaceRecognition.query.get(id)
    if not record:
        return "Record not found", 404

    # Delete the detected face record from the database
    db.session.delete(record)
    db.session.commit()

    # Delete the corresponding image file from the folder
    folder_path = 'images1/' + record.name
    image_filename = f"{record.name}-{record.time.strftime('%Y-%m-%d_%H-%M-%S')}.jpg"
    image_path = os.path.join(folder_path, image_filename)
    if os.path.exists(image_path):
        os.remove(image_path)

    flash('Record deleted successfully', 'success')
    return redirect(url_for('list'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)