from flask import Flask, request, jsonify
import psycopg2

app = Flask(__name__)

# Povezava z bazo PostgreSQL
def get_db_connection():
    conn = psycopg2.connect(
        host="ep-little-resonance-a8axmsnj.eastus2.azure.neon.tech",
        database="picodb",
        user="picodb_owner",
        password="LUnguMyc47ed",
        port="5432"
    )
    return conn

# API klici
@app.route('/mountains', methods=['GET'])
def get_mountains():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''SELECT * FROM mountains''')
    mountains = cursor.fetchall()  # Dobimo seznam
    cursor.close()
    conn.close()
    
    mountains_list = [] #ustvarimo slovar
    for mountain in mountains:
        mountains_list.append({
            "mountain_id": mountain[0],
            "mountain": mountain[1],
            "altitude": mountain[2], 
            "country": mountain[3], 
            "lat": float(mountain[4]),
            "lon": float(mountain[5])
        })

    return jsonify(mountains_list)


@app.route('/visited', methods=['GET'])
def get_visited_mountains():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
                    SELECT mountain, altitude, country, datetime
                    FROM visited v
                   ''')
    visited = cursor.fetchall() #dobimo seznam
    cursor.close()
    conn.close()

    visited_list = []
    for v in visited:
        visited_list.append({
            "mountain": v[0],
            "altitude": v[1],
            "country": v[2],
            "datetime": v[3],
        })

    return jsonify(visited_list)


@app.route('/insert', methods=['POST'])
def insert_data():
    data = request.json
    mountain = data.get('mountain')
    altitude = data.get('altitude')
    country = data.get('country')
    datetime = data.get('datetime')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO visited (mountain, altitude, country, datetime) VALUES (%s, %s, %s, %s)',
                (mountain, altitude, country, datetime))
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({'message': 'Data inserted successfully'})


@app.route('/register', methods=['POST'])
def register():
    data = request.json
    mail = data.get('mail')
    pwd = data.get('pwd')
    user_name = data.get('user_name')

    if not mail or not pwd or not name:
        return jsonify({"status": "error", "message": "Manjkajoči podatki"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    # Preveri, če uporabnik že obstaja
    cur.execute("SELECT * FROM users WHERE mail = %s", (mail,))

    if cur.fetchone():
        cur.close()
        conn.close()
        return jsonify({"status": "error", "message": "Uporabnik že obstaja"}), 400


    # Shrani uporabnika
    cur.execute("INSERT INTO users (mail, psw, user_name) VALUES (%s, %s, %s)",
                (mail, pwd, user_name))
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"status": "ok", "message": "Registracija uspešna"})


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    mail = data.get('mail')
    pwd = data.get('pwd')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT user_name, psw FROM users WHERE mail = %s", (mail,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if user and user[1] == pwd:
        return jsonify({"status": "ok", "user_name": user[0]})
    else:
        return jsonify({"status": "error", "message": "Napačen email ali geslo"}), 401


if __name__ == '__main__':
    app.run(debug=True)
