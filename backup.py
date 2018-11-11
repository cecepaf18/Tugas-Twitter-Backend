from flask import Flask, request, jsonify
import os
from flask_cors import CORS
import psycopg2, psycopg2.extras 

app = Flask(__name__)
cors = CORS(app)

#Membuat koneksi ke database di postgreSQL
con = psycopg2.connect(database=os.getenv('DATABASE'),user=os.getenv('USER'),password=os.getenv('PASSWORD'),host=os.getenv('HOSTDB'),port=os.getenv('PORTDB'))

@app.route('/signUp',methods=['POST'])
def signUp():

    # mengambil data dari frontend
    username = request.json['username']
    fullname = request.json['fullname']
    email = request.json['email']
    password = request.json['password']
    bio = request.json['bio']
    photoprofile = request.json['photoprofile']

    # memasukan data ke database
    cursorSignUp = con.cursor()
    cursorSignUp.execute("Insert into person(username, fullname, email, password, bio, photoprofile) values (%s,%s,%s,%s,%s,%s)",(username,fullname,email,password,bio,photoprofile))
    con.commit()

    return "Sukses", 201

@app.route('/logIn', methods = ['POST'])
def logIn():

    # mengambil data dari frontend
    email = request.json['email']
    password = request.json['password']

    #mengambil data dari database
    cursorLogIn = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursorLogIn.execute("Select * from person where email = %s and password = %s", (email,password))
    jml = cursorLogIn.rowcount

    dataUser = []
    for row in cursorLogIn.fetchall():
        dataUser.append(dict(row))

    con.commit()

    if jml > 0:
        return jsonify(dataUser), 201
    else:
        return "gagal", 400

@app.route('/readTweet', methods = ['GET'])
def readTweet():

    #mengambil data dari database
    cursorReadTweet = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursorReadTweet.execute("select person.id as id, person.username as username, person.fullname as fullname, person.email as email, person.password as password, person.bio as bio, person.photoprofile as photoprofile, tweets.id as idtweet, tweets.content as content, tweets.date as date from tweets inner join person on tweets.person_id=person.id")

    dataTweet = []
    for row in cursorReadTweet.fetchall():
        dataTweet.append(dict(row))

    con.commit()

    return jsonify(dataTweet), 201

@app.route('/readTweetProfile', methods = ['POST'])
def readTweetProfile():
    id = request.json['id']

    #mengambil data dari database
    cursorLogIn = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursorLogIn.execute("select * from person inner join tweets on person.id = tweets.person_id and person.id=%s",(id,))

    dataTweetProfile = []
    for row in cursorLogIn.fetchall():
        dataTweetProfile.append(dict(row))

    con.commit()

    return jsonify(dataTweetProfile), 201


@app.route('/addTweet', methods = ['POST', 'GET'])
def addTweet():
    if request.method == 'POST':

        personId = request.json['id']
        tweet = request.json['content']

        curInsertTweet = con.cursor()
        curInsertTweet.execute("Insert into tweets(content,date,person_id) values (%s,now(),%s)",(tweet, personId))
        con.commit()

        return "Tweet success", 201
    else:
        return "Method Not Allowed", 400

@app.route('/deleteTweet', methods = ['POST', 'GET'])
def deleteTweet():
    if request.method == 'POST':

        idTweet = request.json['idtweet']
        

        curDeleteTweet = con.cursor()
        curDeleteTweet.execute("Delete from tweets where id = %s",(idTweet,))
        con.commit()

        return "Delete Tweet Success", 201
    else:
        return "Method Not Allowed", 400


@app.route('/getFollowing', methods = ['POST'])
def getFollowing():
    id = request.json['id']

    #mengambil data dari database
    cursorgetFollowing = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursorgetFollowing.execute("select * from person where id not in (select following from follow where person_id = %s) and id !=%s",(id,id))

    dataGetFollowing = []
    for row in cursorgetFollowing.fetchall():
        dataGetFollowing.append(dict(row))

    con.commit()

    return jsonify(dataGetFollowing), 201

@app.route('/getProfileHome', methods = ['POST'])
def getProfileHome():
    id = request.json['id']

    cursorgetProfileHome = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursorgetProfileHome.execute("select * from person where id = %s",(id,))

    dataGetProfileHome = []
    for row in cursorgetProfileHome.fetchall():
        dataGetProfileHome.append(dict(row))

    con.commit()

    return jsonify(dataGetProfileHome), 201

@app.route('/addFollow', methods = ['POST', 'GET'])
def addFollow():
    if request.method == 'POST':

        person_id = request.json['person_id']
        idfollowing = request.json['idfollowing']

        curInsertFollow = con.cursor()
        curInsertFollow.execute("Insert into follow(person_id,following) values (%s,%s)",(person_id,idfollowing))
        con.commit()

        return "Follow success", 201
    else:
        return "Method Not Allowed", 400

@app.route('/editProfile',methods=['POST'])
def editProfile():

    # mengambil data dari frontend
    person_id = request.json['id']

    username = request.json['username']
    fullname = request.json['fullname']
    email = request.json['email']
    bio = request.json['bio']

    # memasukan data ke database
    cursorEditProfile = con.cursor()
    cursorEditProfile.execute("Update person set username=%s, fullname=%s, email=%s, bio=%s where id=%s",(username,fullname,email,bio,person_id))
    con.commit()

    return "Edit Account Success", 201

@app.route('/editPassword', methods = ['POST'])
def editPassword():

    id_person = request.json['id']

    currentPass = request.json['currpass']
    newPass = request.json['newpass']
    verifyPass = request.json['verifypass']

    checkingPassword = con.cursor()
    checkingPassword.execute("Select * from person where id = %s and password = %s ",(id_person, currentPass))
    jml = checkingPassword.rowcount
    
    if (jml > 0):
        if verifyPass == newPass:
            currentEditPass = con.cursor()
            currentEditPass.execute("Update person set password=%s where id = %s and password = %s",(newPass, id_person, currentPass))
            con.commit()

            return "Password Edited", 201
        else:
            return "Verify Password and New Password Not Match"
    else:
        return "Password Nothing", 400

    

if __name__=="__main__":
    app.run(debug=True,host=os.getenv('HOST'),port=os.getenv('PORT'))