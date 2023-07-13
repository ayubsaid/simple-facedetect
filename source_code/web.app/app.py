# app.py

from flask import Flask, render_template
import psycopg2

app = Flask(__name__)

# Connect to the PostgreSQL database
conn = psycopg2.connect(
    host="localhost",
    database="postgres",
    user="postgres",
    password="1234"
)
cur = conn.cursor()

# Route to display face records
@app.route('/')
def show_face_records():
    cur.execute("SELECT * FROM face_recognition")
    records = cur.fetchall()
    return render_template('records.html', records=records)

if __name__ == '__main__':
    app.run(port=5001, debug=True)


