import datetime
from flask import Flask, render_template, request, redirect, session, url_for, jsonify
from flask_mysqldb import MySQL

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'abc'

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Ajit123'
app.config['MYSQL_DB'] = 'mydentap'

# Initialize MySQL
mysql = MySQL(app)

# ---------------------- ROUTES ----------------------

# 🟩 LOGIN PAGE
@app.route('/')
def signIn():
    return render_template('signin.html')


# 🟩 LOGIN PROCESS
@app.route('/login', methods=['POST'])
def logIn():
    email = request.form['email']
    password = request.form['pass']
    if email == 'nitya@gmail.com' and password == 'nitya':
        session['email'] = email
        return redirect('/home')
    else:
        return jsonify({'html': '<span>Incorrect Email or Password.</span>'})


# 🟩 HOME PAGE (Today's Appointments)
@app.route('/home')
def home():
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT appointment_id, appointment_time, patient_name, doctor_name
        FROM appointments
        WHERE appointment_date = CURDATE()
    """)
    appointments = cursor.fetchall()
    cursor.close()
    current_date = datetime.date.today().strftime("%B %d, %Y")
    return render_template('index.html', appointments=appointments, current_date=current_date)


# 🟩 ADD PATIENT FORM PAGE
@app.route('/add')
def add():
    return render_template('add.html')


# 🟩 ADD PATIENT PROCESS
@app.route('/addProcess', methods=['POST'])
def addProcess():
    if request.method == 'POST':
        FName = request.form['FName']
        Minit = request.form['Minit']
        LName = request.form['LName']
        Age = request.form['Age']
        ContactNumber = request.form['ContactNumber']
        Address = request.form['Address']

        cur = mysql.connection.cursor()
        cur.callproc('insertPersonalInfo', (FName, Minit, LName, Age, ContactNumber, Address))
        mysql.connection.commit()

        # Insert default appointment for today
        full_name = f"{FName} {LName}"
        today_date = datetime.date.today()
        default_time = "10:00:00"
        default_doctor = "Dr. Sharma"

        cur.execute("""
            INSERT INTO appointments (patient_name, doctor_name, appointment_date, appointment_time, status)
            VALUES (%s, %s, %s, %s, 'Scheduled')
        """, (full_name, default_doctor, today_date, default_time))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('home'))


# 🟩 SEARCH PATIENT
# 🟩 SEARCH PATIENT
@app.route('/searchPatient', methods=['POST'])
def searchPatient():
    search_term = request.form.get('searchMe', '').strip()

    if not search_term:
        return "Please enter a search term"

    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT appointment_id, patient_name, doctor_name, appointment_date, appointment_time, status
        FROM appointments
        WHERE patient_name LIKE %s
    """, (f"%{search_term}%",))
    results = cursor.fetchall()
    cursor.close()

    # No data found
    if not results:
        return "<tr><td colspan='6'>No matching patients found.</td></tr>"

    # Build HTML rows
    html = ""
    for row in results:
        html += f"""
        <tr>
            <td>{row[0]}</td>
            <td>{row[1]}</td>
            <td>{row[2]}</td>
            <td>{row[3]}</td>
            <td>{row[4]}</td>
            <td>{row[5]}</td>
        </tr>
        """
    return html



# 🟩 CUSTOMERS PAGE
@app.route('/customers')
def customers():
    return render_template('customers.html')


# 🟩 UPDATE PATIENT
@app.route('/updateProcess', methods=['POST'])
def updateProcess():
    Fname = request.form['FName']
    Minit = request.form['Minit']
    Lname = request.form['LName']
    Age = request.form['Age']
    Cn = request.form['ContactNumber']
    Address = request.form['Address']
    id = request.form['id']

    if Fname and Minit and Lname and Age and Cn and Address:
        cursor = mysql.connection.cursor()
        cursor.callproc('updatePersonalInfo', (Fname, Minit, Lname, Age, Cn, Address, id))
        mysql.connection.commit()
        cursor.close()
    return ('', 204)


# 🟩 DELETE PATIENT
@app.route('/deleteProcess', methods=['POST'])
def deleteProcess():
    id = request.form['id']
    cursor = mysql.connection.cursor()
    cursor.callproc('deletePatient', (id,))
    mysql.connection.commit()
    cursor.close()
    return redirect('/home')


# 🟩 CALENDAR PAGE
@app.route('/calendar')
def calendar():
    return render_template('calendar.html')


# 🟩 LOGOUT
@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('signIn'))


# 🟩 RESCHEDULE PAGE
@app.route('/reschedule')
def rescheduleAppointment():
    return render_template('reschedule.html')


# 🟩 RESCHEDULE PROCESS
@app.route('/rescheduleProcess', methods=['POST'])
def rescheduleProcess():
    appointment_id = request.form['appointment_id']
    new_date = request.form['new_date']
    new_time = request.form['new_time']

    cursor = mysql.connection.cursor()
    cursor.execute("""
        UPDATE appointments
        SET appointment_date = %s, appointment_time = %s
        WHERE appointment_id = %s
    """, (new_date, new_time, appointment_id))
    mysql.connection.commit()
    cursor.close()

    return redirect(url_for('home'))


# 🟩 CANCEL PAGE
@app.route('/cancel')
def cancel():
    return render_template('cancel.html')


# 🟩 ALERT PATIENTS PAGE
@app.route('/alert_patients')
def alert_patients():
    return render_template('alert_patients.html')


# ---------------------- MAIN ----------------------
if __name__ == '__main__':
    app.run(debug=True)
