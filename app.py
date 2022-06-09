from argparse import Namespace
import email
from flask import Flask, redirect, render_template, session, url_for, request, jsonify
from flask_mail import Mail, Message
import json
from os import environ as env
from urllib.parse import quote_plus, urlencode
import os
from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask_mysqldb import MySQL
from flask_material import Material
from auth0.v3.authentication import Database
import http.client
import base64
from auth0.v3.authentication import GetToken
from auth0.v3.management import Auth0
import requests


ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)
app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")
oauth = OAuth(app)
mail= Mail(app)

app.config['MYSQL_HOST'] = env.get("MYSQL_HOST")
app.config['MYSQL_USER'] = env.get("MYSQL_USER")
app.config['MYSQL_PASSWORD'] = env.get("MYSQL_PASSWORD")
app.config['MYSQL_DB'] = env.get("MYSQL_DB")


mysql = MySQL(app)
Material(app)


#domain = env.get("AUTH0_DOMAIN")
#non_interactive_client_id = env.get("AUTH0_CLIENT_ID"),
#non_interactive_client_secret = env.get("AUTH0_CLIENT_SECRET"),

#get_token = GetToken(domain)
#token = get_token.client_credentials(non_interactive_client_id,
 #   non_interactive_client_secret, 'https://{}/api/v2/'.format(domain))
#print(token)
#mgmt_api_token = token['access_token']


#data = res.read()
#print(data)
#print(data.decode("utf-8"))
# @app.route("/email")
# def index():
#    msg = Message('Hello', sender = ('Englewood Volunteer Ambulance Corp', "englewoodvolunteerambucorp@gmail.com"), recipients = ['allyng9552@gmail.com', 'alyngu22@bergen.org'])
#    msg.body = "TEST!! xxPerson requested a shift from XX to XX on XXX XX, XXXX. Approve?"
#    mail.send(msg)
#    return "Sent"
   
   
# @app.route("/callback", methods=["GET", "POST"])
# def callback():
#     token = oauth.auth0.authorize_access_token()
#     session["user"] = token
#     cursor = mysql.connection.cursor()
#     cursor.execute('''SELECT * FROM user WHERE user_id = %s''', [email])
#     data = cursor.fetchall()
#     print(userid)
#     return redirect("/")

#     return render_template('user.html', data = data)



#Auth0 initial access token
oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
        "aud": ["http://evaccapstone.herokuapp.com/", "http://localhost:3000"],

    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration',
)

#Auth0 Login
@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    return redirect("/")

@app.route("/login")
def loginform():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://"
        + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("main", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )

#Main Page and Forms
@app.route('/')  
def main():
    if('user' in session):
        chunks = session.get("user").get("id_token").split(".")
        chunks[1] += "=" * ((4 - len(chunks[1]) % 4) % 4)
        payload1 = json.loads(base64.urlsafe_b64decode(chunks[1]).decode("utf-8"))
        cursor = mysql.connection.cursor()
        cursor.execute('''SELECT * FROM user WHERE email = %s''', [payload1.get("name")])
        data = cursor.fetchall()
        admin=0
        for row in data:
            if row[12]==1:
                admin=1
        return render_template('main-page.html', admin=admin, data=data, #navigation=navigation,
        session=session.get("user"),
            pretty=json.dumps(session.get("user"), indent=4),
        )
    else:
        return render_template('main-page.html',
        session=session.get("user"),
            pretty=json.dumps(session.get("user"), indent=4),
        )
@app.route('/infoform', methods = ['POST', 'GET'])
def form():
    if('user' in session):
        chunks = session["user"].get("id_token").split(".")
        chunks[1] += "=" * ((4 - len(chunks[1]) % 4) % 4)
        payload1 = json.loads(base64.urlsafe_b64decode(chunks[1]).decode("utf-8"))
        cursor = mysql.connection.cursor()
        cursor.execute('''SELECT * FROM user WHERE email = %s''', [payload1.get("name")])
        data = cursor.fetchall()
        admin=0
        for row in data:
            if row[12]==1:
                admin=1
        if request.method == 'GET':
            return render_template('my-info.html', admin=admin, data=data, session=session.get("user"),
                pretty=json.dumps(session.get("user"), indent=4),
            )

        
        if request.method == 'POST':
            name = request.form['name']
            surname = request.form['surname']
            bday = request.form['birthdate']
            phone = request.form['mobile number']
            address1 = request.form['address1']
            address2 = request.form['address2']

            email = request.form['email']
            print(cursor.execute('''SELECT COUNT(*) FROM user WHERE email = email'''))

            if cursor.execute('''SELECT COUNT(*) FROM user WHERE email = email''') > 0: 

                oldemail = session["user"].get("userinfo").get("email")
                if phone != "":
                    cursor.execute('''UPDATE user SET phonenum = %s WHERE email = %s''',(phone,oldemail))
                if address1 != "":
                    cursor.execute('''UPDATE user SET address = %s WHERE email = %s''',(address1, oldemail))    
                if address2 != "":
                    cursor.execute('''UPDATE user SET city = %s WHERE email = %s''',(address2,oldemail))
            else:
                big = cursor.execute('''SELECT user_id FROM user''') + 1
                cursor.execute(''' INSERT INTO user VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, %s, %s)''',((big+1), name,surname, bday, address1, address2, email, phone,0, 0, 0, 0))
            #UPDATE Customers
            #SET ContactName = 'Alfred Schmidt', City= 'Frankfurt'
            #WHERE CustomerID = 1;        
            cursor.execute('''SELECT * FROM user WHERE email = %s''', [payload1.get("name")])
            data=cursor.fetchall()
            mysql.connection.commit()
            cursor.close()
            return render_template('my-info.html', admin=admin, data=data,
            session=session.get("user"),
                pretty=json.dumps(session.get("user"), indent=4),
            )
    else:
        return redirect("/")
        

@app.route('/create', methods = ['POST', 'GET'])
def create():
    if('user' in session):
        chunks = session["user"].get("id_token").split(".")
        chunks[1] += "=" * ((4 - len(chunks[1]) % 4) % 4)
        payload1 = json.loads(base64.urlsafe_b64decode(chunks[1]).decode("utf-8"))
        cursor = mysql.connection.cursor()
        cursor.execute('''SELECT * FROM user WHERE email = %s''', [payload1.get("name")])
        data = cursor.fetchall()

        for row in data:
            if row[12]==0:
                return render_template("404.html")
        
        if request.method == 'GET':
            return render_template('createuser.html', exists = 0, data=data, session=session.get("user"),
            pretty=json.dumps(session.get("user"), indent=4),
        )
        
        if request.method == 'POST':
            name = request.form['name']
            surname = request.form['surname']
            bday = request.form['birthdate']
            phone = request.form['mobile number']
            address1 = request.form['address1']
            address2 = request.form['address2']
            email = request.form['email']
            admin = request.form.get("admin", None)
            admin = str(admin)
            cursor = mysql.connection.cursor()
            chunks = session["user"].get("id_token").split(".")
            chunks[1] += "=" * ((4 - len(chunks[1]) % 4) % 4)
            payload1 = json.loads(base64.urlsafe_b64decode(chunks[1]).decode("utf-8"))
            cursor.execute('''SELECT * FROM user WHERE email = %s''', [payload1.get("name")])
            data=cursor.fetchall()

            cursor.execute('''SELECT * FROM user WHERE email = %s''', [email])
            p = cursor.fetchall()
            for row in data:
                oldemail = row[1]
            if oldemail == email:
                return render_template("createuser.html", exists=1, data=data, session=session.get("user"),
                pretty=json.dumps(session.get("user"), indent=4),)
            elif len(p)>0:
                return render_template("createuser.html", exists=1, data=data, session=session.get("user"),
                pretty=json.dumps(session.get("user"), indent=4),)
            else:
                big = cursor.execute('''SELECT user_id FROM user''') + 1
                cursor.execute(''' INSERT INTO user VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, %s, %s, %s)''',((big+1), name,surname, bday, address1, address2, email, phone,0, 0, 0, 0, admin)) 
            mysql.connection.commit()
        
            cursor.close()
            return render_template('createuser.html', data=data, exists=0,session=session.get("user"),
                pretty=json.dumps(session.get("user"), indent=4),
            )
        else:
            return redirect("/")

@app.route('/rigform', methods = ['POST', 'GET'])
def rigform():
    if('user' in session):
        chunks = session["user"].get("id_token").split(".")
        chunks[1] += "=" * ((4 - len(chunks[1]) % 4) % 4)
        payload1 = json.loads(base64.urlsafe_b64decode(chunks[1]).decode("utf-8"))
        cursor = mysql.connection.cursor()
        cursor.execute('''SELECT * FROM user WHERE email = %s''', [payload1.get("name")])
        data = cursor.fetchall()
        print(data)
        admin=0
        for row in data:
            if row[12]==1:
                admin=1
        if request.method == 'GET':
            return render_template('rig-check.html', admin=admin, data=data, session=session.get("user"), pretty=json.dumps(session.get("user"), indent=4)) 
        if request.method == 'POST':
            dispatchNum = request.form['dispatcher']
            chief = request.form['chief']
            day = request.form['day']
            name1 = request.form['name1']
            name2 = request.form['name2']
            name3 = request.form['name3']
            name4 = request.form['name4']

            radioNum = request.form['radioNum']
            caseNum= request.form['caseNum']
            strapNum= request.form['strapNum']
            micNum= request.form['micNum']
            dutyPagerNum= request.form['dutyPagerNum']
            genPagerNum = request.form['genPagerNum']

            numLight= request.form['numLight']
            rigBag= request.form.get("rigBag", None)
            suction= request.form.get("suction", None)
            defibAd= request.form.get("defibAd",None)
            defibPed= request.form.get("defibPed",None)
            o2a= request.form.get("o2a",None)
            o2b= request.form.get("o2b",None)
            trauma= request.form.get("trauma",None)
            pediBag= request.form.get("pediBag",None)
            scoop= request.form.get("scoop",None)
            stairChar = request.form.get("stairChair",None)
            backboards = request.form.get("backboards",None)
            pediboard = request.form.get("pediBoard",None)
            collarBag = request.form.get("collarBag",None)
            ked = request.form.get("ked",None)
            narccan = request.form.get("narccan",None)
            epipen = request.form.get("epipen",None)
            glucose = request.form.get("glucose",None)

            comments = request.form['comments']
            
            cursor = mysql.connection.cursor()
            
            cursor.execute('''SELECT user_id FROM user WHERE name = %s''', [chief])
            chief_id = cursor.fetchone()

            cursor.execute('''SELECT user_id FROM user WHERE name = %s''', [name1])
            id1 = cursor.fetchone()
            
            cursor.execute('''SELECT user_id FROM user WHERE name = %s''', [name2])
            id2 = cursor.fetchone()
            cursor.execute('''SELECT user_id FROM user WHERE name = %s''', [name3])
            id3 = cursor.fetchone()
            cursor.execute('''SELECT user_id FROM user WHERE name = %s''', [name4])
            id4 = cursor.fetchone()
            cursor.execute('''SELECT shift_id FROM calendar WHERE date = %s''', [day])
            shift_id = cursor.fetchone()

            big = cursor.execute('''SELECT rig_check_id FROM rigcheck''') + 1
            cursor.execute(''' INSERT INTO rigcheck VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(big, shift_id, day, dispatchNum,
            chief_id, id1, id2, id3, id4, radioNum, caseNum, strapNum, micNum, dutyPagerNum, genPagerNum, numLight, rigBag,
            suction, defibPed, defibAd, o2a, o2b, trauma, pediBag, scoop, stairChar, backboards, pediboard, collarBag, ked, narccan,
            epipen, glucose, comments))
            mysql.connection.commit()
            
            cursor.close()
            return render_template('rig-check.html', admin=admin, data=data,
            session=session.get("user"), 
                pretty=json.dumps(session.get("user"), indent=4),
            )
    else:
        return redirect("/")

@app.route('/clockin', methods = ['POST', 'GET'])
def clockform():
    if('user' in session):
        chunks = session["user"].get("id_token").split(".")
        chunks[1] += "=" * ((4 - len(chunks[1]) % 4) % 4)
        payload1 = json.loads(base64.urlsafe_b64decode(chunks[1]).decode("utf-8"))
        cursor = mysql.connection.cursor()
        cursor.execute('''SELECT * FROM user WHERE email = %s''', [payload1.get("name")])
        data = cursor.fetchall()
        admin=0
        for row in data:
            if row[12]==1:
                admin=1
        if request.method == 'GET':
            return render_template('clock-in.html', data=data, admin=admin, session=session.get("user"), pretty=json.dumps(session.get("user"), indent=4),)
        if request.method == 'POST':
            date = request.form['day']
            time = request.form['time']
            name1 = request.form['name1']
            name2 = request.form['name2']
            name3 = request.form['name3']
            name4 = request.form['name4']
            infolist = [date, time, name1, name2]
            for i in infolist:
                if i=="":
                    return render_template("clock-in.html", empty=1, data=data, admin=admin, session=session.get("user"),
                    pretty=json.dumps(session.get("user"), indent=4),)
            cursor = mysql.connection.cursor()

            cursor.execute('''SELECT user_id FROM user WHERE name = %s''', [name1])
            id1 = cursor.fetchone()
            
            cursor.execute('''SELECT user_id FROM user WHERE name = %s''', [name2])
            id2 = cursor.fetchone()
            cursor.execute('''SELECT user_id FROM user WHERE name = %s''', [name3])
            id3 = cursor.fetchone()
            cursor.execute('''SELECT user_id FROM user WHERE name = %s''', [name4])
            id4 = cursor.fetchone()

            
            # if time < "12:00" and time > "6:00":
            #     type = "6am"
            # elif time > "12:00" and time < "18:00":
            #     type= "12pm"
            # elif time > "18:00" and time < "6:00":
            #     type = "6pm"
            # else:
            #     type = "12am"
            type = "6am"
            cursor.execute('''SELECT shift_id FROM calendar WHERE date = %s AND shift_type = %s''', [date, type])
            shift_id = cursor.fetchone()

            list = [id1, id2, id3, id4]
            for id in list:
                cursor.execute("UPDATE user SET qstipend = qstipend+25 WHERE user_id = %s", [id])
                cursor.execute("UPDATE user SET tstipend = tstipend+25 WHERE user_id = %s", [id])
                cursor.execute("UPDATE user SET qhours = qhours+12 WHERE user_id = %s", [id])
                cursor.execute("UPDATE user SET thours = thours+12 WHERE user_id = %s", [id])


            cursor.execute(''' INSERT INTO clockin VALUES(%s,%s,%s,%s,%s,%s,%s,%s)''',(shift_id, date, time, id1, id2, id3, id4, type))
            # if shift_id is not None:
            #     mysql.connection.commit()
            
            cursor.close()
            return render_template('clock-in.html', data=data, admin=admin,
            session=session.get("user"), 
                pretty=json.dumps(session.get("user"), indent=4))
    else:
        return redirect("/")

@app.route('/calendarform')
def calendar():
    # cursor = mysql.connection.cursor()

    # cursor.execute('''SELECT * FROM calendar''')
    # all = cursor.fetchall()
    # events = []
    # for event in all:
    #     dateList = event[2].split("-")
    #     date = (int(dateList[0]), int(dateList[1]), int(dateList[2]))
    #     events.append([date, str(event[3]), str(event[1])])
    # print(events)
    # return render_template('calendar.html')
    if('user' in session):    
        cursor = mysql.connection.cursor()

        cursor.execute('''SELECT * FROM calendar''')
        all = cursor.fetchall()
        events = []
        for event in all:
            dateList = event[2].split("-")
            date = [int(dateList[0]), int(dateList[1])-1, int(dateList[2])]
            cursor.execute('''SELECT name FROM user WHERE user_id = %s''', [event[1]])
            user = cursor.fetchone()
            events.append([date, event[3], user])
        print(events)
        chunks = session["user"].get("id_token").split(".")
        chunks[1] += "=" * ((4 - len(chunks[1]) % 4) % 4)
        payload1 = json.loads(base64.urlsafe_b64decode(chunks[1]).decode("utf-8"))
        cursor.execute('''SELECT * FROM user WHERE email = %s''', [payload1.get("name")])
        currentuser = cursor.fetchall()
        admin=0
        for row in currentuser:
            if row[12]==1:
                admin=1
        return render_template('calendar.html', admin=admin, currentuser=currentuser, events = events)
    else:
        return redirect("/")
#Data Displays

@app.route('/rigcheck-data')
def rigcheck_data():
    chunks = session["user"].get("id_token").split(".")
    payload1 = json.loads(base64.urlsafe_b64decode(chunks[1]).decode("utf-8"))
    cursor = mysql.connection.cursor()
    cursor.execute('''SELECT * from rigcheck''')
    data = cursor.fetchall()
    for row in data:
            if row[12]==0:
                return render_template("404.html")
    return render_template('rigs.html', data = data)

@app.route('/user/<userid>')
def userfunc(userid):
    if('user' in session):    
        cursor = mysql.connection.cursor()
        cursor.execute('''SELECT * FROM user WHERE user_id = %s''', [userid])
        data = cursor.fetchall()
        chunks = session["user"].get("id_token").split(".")
        chunks[1] += "=" * ((4 - len(chunks[1]) % 4) % 4)
        payload1 = json.loads(base64.urlsafe_b64decode(chunks[1]).decode("utf-8"))
        cursor = mysql.connection.cursor()
        cursor.execute('''SELECT * FROM user WHERE email = %s''', [payload1.get("name")])
        username = cursor.fetchall()
        for row in data:
            if row[12]==0:
                return render_template("404.html")
        return render_template('user.html', data = data, username=username)
    else:
        return redirect("/")

@app.route('/schedule')
def schedule_dispay():
    if('user' in session):
        cursor = mysql.connection.cursor()
        chunks = session["user"].get("id_token").split(".")
        chunks[1] += "=" * ((4 - len(chunks[1]) % 4) % 4)
        payload1 = json.loads(base64.urlsafe_b64decode(chunks[1]).decode("utf-8"))
        cursor.execute('''SELECT * FROM user WHERE email = %s''', [payload1.get("name")])
        currentuser = cursor.fetchall()
        cursor.execute('''SELECT * FROM calendar''')
        data = cursor.fetchall()
        
        cursor.execute('''SELECT user_id FROM calendar''')
        userids = cursor.fetchall()
        names= []
        for id in userids:
            cursor.execute('''SELECT name FROM user WHERE user_id = %s''', [id])
            names.append(cursor.fetchone())
        for row in currentuser:
            if row[12]==0:
                return render_template("404.html")
        return render_template('schedule_display.html', currentuser=currentuser, data = data, names = names)
    else:
        return redirect("/")
@app.route('/clockdisplay')
def clock_display():
    if('user' in session):
        cursor = mysql.connection.cursor()
        chunks = session["user"].get("id_token").split(".")
        chunks[1] += "=" * ((4 - len(chunks[1]) % 4) % 4)
        payload1 = json.loads(base64.urlsafe_b64decode(chunks[1]).decode("utf-8"))
        cursor.execute('''SELECT * FROM user WHERE email = %s''', [payload1.get("name")])
        currentuser = cursor.fetchall()
        cursor.execute('''SELECT * FROM clockin''')
        data = cursor.fetchall()
        for row in currentuser:
            if row[12]==0:
                return render_template("404.html")
        return render_template('clock-display.html', currentuser=currentuser, data = data)
    else:
        return redirect("/")

@app.route('/users')
def users():
    if('user' in session):
        cursor = mysql.connection.cursor()
        cursor.execute('''SELECT * from user''')
        data = cursor.fetchall()
        chunks = session["user"].get("id_token").split(".")
        chunks[1] += "=" * ((4 - len(chunks[1]) % 4) % 4)
        payload1 = json.loads(base64.urlsafe_b64decode(chunks[1]).decode("utf-8"))
        cursor.execute('''SELECT * FROM user WHERE email = %s''', [payload1.get("name")])
        info = cursor.fetchall()
        for row in info:
            if row[12]==0:
                return render_template("404.html")
        return render_template('user.html', info=info, data = data)
    else:
        return redirect("/")


@app.route('/calendar', methods = ['POST', 'GET'])
def calendarCheck():
    if('user' in session):
        cursor = mysql.connection.cursor()
        chunks = session["user"].get("id_token").split(".")
        chunks[1] += "=" * ((4 - len(chunks[1]) % 4) % 4)
        payload1 = json.loads(base64.urlsafe_b64decode(chunks[1]).decode("utf-8"))
        cursor.execute('''SELECT * FROM user WHERE email = %s''', [payload1.get("name")])
        currentuser = cursor.fetchall()
        print(currentuser)
        admin=0
        for row in currentuser:
            if row[12]==1:
                admin=1
        if request.method == 'GET':
            cursor.execute('''SELECT * FROM calendar''')
            all = cursor.fetchall()
            events = []
            for event in all:
                dateList = event[2].split("-")
                date = [int(dateList[0]), int(dateList[1])-1, int(dateList[2])]
                cursor.execute('''SELECT name FROM user WHERE user_id = %s''', [event[1]])
                user = cursor.fetchone()
                events.append([date, event[3], user])
            print(events)
            return render_template('calendar.html', admin=admin, currentuser=currentuser, events = events)
        if request.method == 'POST':
            date = request.form['date']
            shift = request.form.get("shift_type", None)
            name = request.form['name']
        
            cursor = mysql.connection.cursor()
            
            cursor.execute('''SELECT user_id FROM user WHERE name = %s''', [name])
            id = cursor.fetchone()
            
            shift_id = cursor.execute('''SELECT shift_id FROM calendar''') + 1
            cursor.execute('''INSERT INTO calendar VALUES(%s, %s, %s, %s, %s)''', (shift_id, id, date, shift, 1))
            mysql.connection.commit()
            cursor.execute('''SELECT * FROM calendar''')
            all = cursor.fetchall()
            events = []
            for event in all:
                dateList = event[2].split("-")
                date = [int(dateList[0]), int(dateList[1])-1, int(dateList[2])]
                cursor.execute('''SELECT name FROM user WHERE user_id = %s''', [event[1]])
                user = cursor.fetchone()
                events.append([date, event[3], user])
            cursor.close()
            return render_template('calendar.html',
            currentuser=currentuser, admin=admin, events = events, session=session.get("user"),
                pretty=json.dumps(session.get("user"), indent=4),
            )
    else:
        return redirect("/")
    

@app.route('/data')
def data():
    cursor = mysql.connection.cursor()
    chunks = session["user"].get("id_token").split(".")
    chunks[1] += "=" * ((4 - len(chunks[1]) % 4) % 4)
    payload1 = json.loads(base64.urlsafe_b64decode(chunks[1]).decode("utf-8"))
    cursor.execute('''SELECT * FROM user WHERE email = %s''', [payload1.get("name")])
    currentuser = cursor.fetchall()
    cursor.execute('''SELECT * FROM clockin''')
    for row in currentuser:
        if row[12]==0:
            return render_template("404.html")
    return render_template('data.html', currentuser=currentuser, session=session.get("user"), pretty=json.dumps(session.get("user"), indent=4),)


app.debug = True
app.run(host="0.0.0.0", port=env.get("PORT", 3000))

