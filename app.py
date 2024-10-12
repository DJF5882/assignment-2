from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


app = Flask(__name__)

mysql_credentials = os.getenv("MYSQL_CREDENTIALS")

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = mysql_credentials
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

# Initialize the database
db = SQLAlchemy(app)

# Define the Reservation model
class Reservation(db.Model):
    __tablename__ = 'reservations'
    id = db.Column(db.Integer, primary_key=True)
    car_type = db.Column(db.String(50), nullable=False)
    driver_name = db.Column(db.String(100), nullable=False)
    pick_up = db.Column(db.DateTime, nullable=False)
    drop_off = db.Column(db.DateTime, nullable=False)

    def __init__(self, car_type, driver_name, pick_up, drop_off):
        self.car_type = car_type
        self.driver_name = driver_name
        self.pick_up = pick_up
        self.drop_off = drop_off

# Route to show the list of reservations
@app.route('/')
def reservation_list():
    reservations = Reservation.query.all()  # Get all reservations from the database
    return render_template('reservation_list.html', reservations=reservations)

# Route to handle reservation form
@app.route('/make_reservation', methods=['GET', 'POST'])
def make_reservation():
    if request.method == 'POST':
        car_type = request.form['car_type']
        driver_name = request.form['driver_name']
        pick_up = request.form['pick_up']
        drop_off = request.form['drop_off']

        # Parse datetime-local format
        pick_up_datetime = datetime.strptime(pick_up, '%Y-%m-%dT%H:%M')
        drop_off_datetime = datetime.strptime(drop_off, '%Y-%m-%dT%H:%M')

        # Validate that pick-up time is at least 24 hours in the future
        if pick_up_datetime < datetime.now() + timedelta(hours=24):
            return "Reservation must be made at least 24 hours in advance", 400

        # Create a new reservation and add it to the database
        new_reservation = Reservation(
            car_type=car_type,
            driver_name=driver_name,
            pick_up=pick_up_datetime,
            drop_off=drop_off_datetime
        )
        db.session.add(new_reservation)
        try:
            db.session.commit()
            print("Data committed successfully!")
        except Exception as e:
            db.session.rollback()  # Rollback the session if there's an error
            print(f"Error occurred: {e}")

        return redirect(url_for('reservation_list'))
    
    return render_template('reservation_form.html')

if __name__ == '__main__':
    # Create the database tables if they don't exist yet
    db.create_all()

    # Run the Flask app
    app.run(debug=True)
