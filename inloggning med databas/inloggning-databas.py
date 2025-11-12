from flask import Flask, render_template, session, redirect, url_for, request
import mysql.connector 
app = Flask(__name__)
app.secret_key = 'hemligtextsträngsomingenkangissa' 

def get_connection(host="localhost", user="root", password=""):
    mydb = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database="webbserverprogrammering" 
    )
    return mydb

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        logged_in = False
        db = get_connection()
        mycursor = db.cursor()
        mycursor.execute("SELECT * FROM users")
        users = mycursor.fetchall()
        for user in users:
            
           
            if request.form['name'] == user[0] and request.form['password'] == user[1]:
                logged_in = True
                session['user'] = {'username': user[0], 'email': user[2]}
                break
        if not logged_in: 
            session.clear()
        return redirect(url_for('login'))
    
   
    return render_template('home.html')

@app.route('/login')
def login():
    if session:
        return render_template('login.html', user=session['user'])
    else:
        return render_template('error.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        email = request.form.get('email', '').strip()

        if not username or not password:
            return render_template('register.html', error='Fyll i användarnamn och lösenord')

        db = get_connection()
        cursor = db.cursor()
      
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            cursor.close()
            db.close()
            return render_template('register.html', error='Användarnamn finns redan')

       
        cursor.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)",
                       (username, password, email))
        db.commit()
        cursor.close()
        db.close()

        return redirect(url_for('index'))

    return render_template('register.html')

@app.route('/append', methods=['POST'])
def append():
    if not session:
        return render_template('error.html')
    
    message = request.form.get('line', '')
    username = session['user']['username']
    
    db = get_connection()
    cursor = db.cursor()
    sql = "INSERT INTO messages (username, message) VALUES (%s, %s)"
    values = (username, message)
    cursor.execute(sql, values)
    db.commit()
    cursor.close()
    db.close()
    
    return redirect('/annansida')

@app.route('/annansida')
def annansida():
    if session:
        db = get_connection()
        cursor = db.cursor()
        cursor.execute("SELECT username, message, created_at FROM messages ORDER BY created_at DESC")
        messages = cursor.fetchall()
        cursor.close()
        db.close()
        return render_template('annansida.html', user=session['user'], messages=messages)
    else:
        return render_template('error.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')