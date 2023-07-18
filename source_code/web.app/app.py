from flask import Flask, render_template
import psycopg2
import base64

app = Flask(__name__, template_folder='', static_folder='static')

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

    # Convert image data to Base64 and update the record
    records_with_images = []
    for record in records:
        image_data = record[3].tobytes()
        image_base64 = base64.b64encode(image_data).decode("utf-8")
        record_with_image = list(record)
        record_with_image[3] = f"data:image/jpeg;base64,{image_base64}"
        records_with_images.append(record_with_image)

    return render_template('records.html', records=records_with_images)

if __name__ == '__main__':
    app.run(port=5001, debug=True)