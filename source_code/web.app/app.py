from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import base64

app = Flask(__name__, template_folder='', static_folder='static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost/postgres'
app.secret_key = 'mysecretkey'
db = SQLAlchemy(app)

# Define the model for the face_recognition table
class FaceRecognition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.TIMESTAMP)
    name = db.Column(db.String(255))
    image_data = db.Column(db.LargeBinary)

# Define the model for the users table
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    last_login = db.Column(db.TIMESTAMP, default=datetime.utcnow)

    # Specify the custom table name "users"
    __tablename__ = "users"

# Route to display face records with pagination
@app.route('/')
def show_face_records():
    # Check if user is logged in
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))

    page = request.args.get('page', 1, type=int)
    per_page = 7  # Number of records per page

    records = FaceRecognition.query.order_by(FaceRecognition.time.desc()).paginate(page=page, per_page=per_page)

    # Convert image data to Base64 and update the record
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

    return render_template('records.html', records=records_with_images, pagination=records)

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username and password match in the database
        user = User.query.filter_by(username=username, password=password).first()

        if user:
            # Set the session variable to indicate that the user is logged in
            session['logged_in'] = True
            # Update the last login time for the user
            user.last_login = datetime.utcnow()
            db.session.commit()
            return redirect(url_for('show_face_records'))
        else:
            return render_template('login.html', message="Invalid username or password")

    return render_template('login.html')

@app.route('/logout', methods=['POST'])
def logout():
    # Clear the session data
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(port=5003, debug=True)
