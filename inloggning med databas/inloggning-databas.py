from flask import Flask, render_template, session, redirect, url_for, request
import mysql.connector  # installera med "pip install mysql-connector-python" i kommandotolken, ifall du inte redan gjort detta

app = Flask(__name__)
app.secret_key = 'hemligtextsträngsomingenkangissa'  # Används för sessionshantering

# skapa databasuppkoppling
def get_connection(host="localhost", user="root", password=""):
    mydb = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database="webbserverprogrammering"  # byt namn om din databas heter något annat
    )
    return mydb

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # kontrollera att inloggningsuppgifter stämmer
        logged_in = False
        db = get_connection()
        mycursor = db.cursor()
        mycursor.execute("SELECT * FROM users")
        users = mycursor.fetchall()
        for user in users:
            
            # varje user i loopen är en 4-tippel på formen (username, password, email, id)
            if request.form['name'] == user[0] and request.form['password'] == user[1]:
                # i själva verket bör inte lösenord lagras i klartext utan vara krypterade - mer om detta senare i kursen
                logged_in = True
                session['user'] = {'username': user[0], 'email': user[2]}
                break
        if not logged_in: # om hela loopen har gått utan att någon matchning hittats
            session.clear()
        return redirect(url_for('login'))
    
    # Det här returneras om GET-anrop görs
    return render_template('home.html')

@app.route('/login')
def login():
    if session:
        return render_template('login.html', user=session['user'])
    else:
        return render_template('error.html')

@app.route('/annansida')
def annansida():
    if session:
        return render_template('annansida.html', user=session['user'])
    else:
        return render_template('error.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/append', methods=['POST'])
def append():
    if not session: # om man inte är inloggad
        return render_template('error.html')
    line = f'{session['user']['username']} skrev: {request.form.get('line', '')}'
    with open('meddelanden.txt', 'a', encoding='utf-8') as f:
        f.write(line + '\n')
    return redirect('/annansida')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')