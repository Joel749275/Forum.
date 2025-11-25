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
        username = request.form.get('name', '').strip()
        password = request.form.get('password', '').strip()
        db = get_connection()
        cur = db.cursor()
        cur.execute("SELECT id, username, password, email FROM users WHERE username = %s", (username,))
        row = cur.fetchone()
        cur.close()
        db.close()
        if row and password == row[2]:
            session['user'] = {'id': row[0], 'username': row[1], 'email': row[3]}
        else:
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
    topic_id = request.form.get('topic_id') 
    user_id = session['user']['id']
    username = session['user']['username']
    
    db = get_connection()
    cursor = db.cursor()
    if topic_id:
        cursor.execute("INSERT INTO messages (topic_id, user_id, username, message) VALUES (%s, %s, %s, %s)",
                       (topic_id, user_id, username, message))
    else:
        cursor.execute("INSERT INTO messages (user_id, username, message) VALUES (%s, %s, %s)",
                       (user_id, username, message))
    db.commit()
    cursor.close()
    db.close()
    if topic_id:
        return redirect(url_for('view_topic', topic_id=topic_id))
    return redirect('/annansida')

@app.route('/topics', methods=['GET', 'POST'])
def topics():
    if request.method == 'POST':
        if not session:
            return render_template('error.html')
        title = request.form.get('title', '').strip()
        if not title:
            return redirect(url_for('topics'))
        db = get_connection()
        cur = db.cursor()
        cur.execute("INSERT INTO topics (title, creator_id) VALUES (%s, %s)", (title, session['user']['id']))
        db.commit()
        topic_id = cur.lastrowid
        cur.close()
        db.close()
        return redirect(url_for('view_topic', topic_id=topic_id))

    db = get_connection()
    cur = db.cursor()
    cur.execute("SELECT id, title, created_at FROM topics ORDER BY created_at DESC")
    topics = cur.fetchall()
    cur.close()
    db.close()
    return render_template('topics.html', user=session.get('user'), topics=topics)

@app.route('/topic/<int:topic_id>', methods=['GET', 'POST'])
def view_topic(topic_id):
    db = get_connection()
    cur = db.cursor()
    if request.method == 'POST':
        if not session:
            cur.close()
            db.close()
            return render_template('error.html')
        content = request.form.get('content', '').strip()
        if content:
            cur.execute(
                "INSERT INTO messages (topic_id, user_id, username, message) VALUES (%s, %s, %s, %s)",
                (topic_id, session['user']['id'], session['user']['username'], content)
            )
            db.commit()
    cur.execute("SELECT id, title, created_at FROM topics WHERE id = %s", (topic_id,))
    topic = cur.fetchone()
    if not topic:
        cur.close()
        db.close()
        return render_template('error.html')
    cur.execute("SELECT username, message, created_at FROM messages WHERE topic_id = %s ORDER BY created_at ASC", (topic_id,))
    posts = cur.fetchall()
    cur.close()
    db.close()
    return render_template('topic.html', user=session.get('user'), topic=topic, posts=posts)

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