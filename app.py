from flask import Flask, render_template, url_for, request, redirect
from flask.globals import request, session
import mysql.connector
import datetime
import random
import re
from mysql.connector import connect, Error

app = Flask(__name__)

app.secret_key = 'Short URL secret key'
class dbcurd:
    def __init__(self):   
        try:
            self.connection = connect(
            host="localhost",
            user="root",
            password="Arjun1234",
            database = "urlShortner",
            )
        except Error as e:
            print (e)
            print("Task as been terminated")
        else:
            print("connected to DB")
    
    def duplicatecheck(self,acURL):
        curr = self.connection.cursor(); 
        select_row = (f'SELECT * FROM URL_INFO WHERE ACTUAL_URL="{acURL}"')
        curr.execute(select_row)
        myresult = curr.fetchall()
        if(len(myresult)>0):
            return myresult[0]
        else:
            return 0;

    def fetchActual(self,hashString):
        curr = self.connection.cursor();
        search_for = (f'SELECT * FROM URL_INFO WHERE SHORT_URL="{hashString}"')
        curr.execute(search_for)
        result = curr.fetchall()
        if(len(result)>0):
            return result[0]
        else:
            return 0

    def insertToDb(self,actualUrl,shortUrl):
        curr = self.connection.cursor()
        sql = "INSERT INTO URL_INFO VALUES (%s, %s, %s)"
        val = (f"{actualUrl}",f"{shortUrl}",0)
        try:
            curr.execute(sql,val)
            self.connection.commit()
        except Error as e:
            print(e)
    def updateHitCount(self,actualUrl):
        curr = self.connection.cursor()
        url,shrtur,hitcount = self.duplicatecheck(actualUrl)
        hitcount+=1
        sql = f'UPDATE URL_INFO SET HIT_COUNT={hitcount} WHERE ACTUAL_URL ="{url}"'
        curr.execute(sql)
        self.connection.commit()

    def validate(self,url):
        if(re.search("http://",url) or re.search("https://",url)):
            print("valid URL")
            return 1
        else:
            print("Invalid URL")
            return 0

    def userLogin(self,userName, Password):
        curr = self.connection.cursor()
        curr.execute('SELECT * FROM USERS WHERE UserName = %s AND UserPass = %s',(userName, Password ))
        # sql = f'SELECT * FROM USERS WHERE UserName="{userName}"" AND UserPass={Password}'
        
        # curr.execute(sql)
        account = curr.fetchone()
        return account
    # except:
        # False


            
    
    def userRegister(self,userName,Password,emailId):
        curr = self.connection.cursor(); 
        sql = "INSERT INTO USERS VALUES (NULL,%s, %s, %s, %s)"
        val = (f"{userName}",f"{Password}",f"{emailId}",0)
        try:
            curr.execute(sql,val)
            self.connection.commit()
            return True

        except:
            return False

        

    def fetchclone(self,userName):
        curr = self.connection.cursor(); 
        search_for = (f'SELECT * FROM USERS WHERE UserName="{userName}"')
        curr.execute(search_for)
        account = curr.fetchone()
        if(account):return 1
        else:
             return 0

    def incrementUrlCount(self,userName):
        curr = self.connection.cursor()
        search_for = (f'SELECT * FROM USERS WHERE UserName="{userName}"')
        curr.execute(search_for)
        account = curr.fetchone()
        id,name,paswd,email,count = account
        count+=1
        sql = f'UPDATE USERS SET UrlCnt={count} WHERE UserName ="{userName}"'
        curr.execute(sql)
        self.connection.commit()

    def getDashBoardData(self,userName):
        curr = self.connection.cursor()
        search_for = (f'SELECT * FROM USERS WHERE UserName="{userName}"')
        curr.execute(search_for)
        account = curr.fetchone()
        id,name,paswd,email,count = account
        return count;



class ShortUrl():
    def __init__(self,inputUrl,domain):
#         dbmsCURD.__init__(self)
        self.url = inputUrl;   
        self.domain = domain
    def genShUrl(self):
#         hashh = hashlib.sha3_224();
        length = len(self.url)
#         print(length);
        date =str(datetime.datetime.now());
        hashValue = abs(int((hash(date))));
        hashValue2 =abs(int(hash(self.url)))
#         print(hashValue,hashValue2)
        hashString = ""
        itterate = random.randrange(2,4)
        while(itterate):
            hashString+=(chr(int(hashValue % 26)+random.choice([65,97])))
            if(not hashValue):
                break
            hashValue /= 26
            hashString+=(chr(int(hashValue % 26)+random.choice([65,97])))
            if(not hashValue):
                break
            hashValue /= 26
            itterate -=1;
        shortUrl = f'{self.domain}/{hashString}'           
        print(shortUrl)
        return shortUrl
@app.route('/dashBoard',methods=['GET','POST'])
def dashBoard():
    db = dbcurd()
    if(session):
        totalCount = db.getDashBoardData(session['username'])
        return render_template("dashboard.html", count=totalCount)
    else:
        return "Invalid Session"    
 


@app.route('/shortUrl',methods=['GET','POST'])
def shortUrl():
    if(session):
        if request.method == 'POST':
            inputUrl = request.form['content']
            print(inputUrl)
            db = dbcurd()
            if(db.validate(inputUrl)):
                if(db.duplicatecheck(inputUrl)):
                    shrturl=(db.duplicatecheck(inputUrl))[1]
                    print("short URL already exist for URL",inputUrl,"is",shrturl)
                    return render_template("shrturl.html", url=shrturl)
                else:
                    print("generating new short URL")
                    createUrl = ShortUrl(inputUrl,"http://127.0.0.1:5000")
                    shortUrl = createUrl.genShUrl()
                    while(db.fetchActual(shortUrl)):
                        shortUrl = createUrl.genShUrl()
                    if(not( db.fetchActual(shortUrl))):
                        db.insertToDb(inputUrl,shortUrl)    
                    print("fetched Actual url for shortUrl",shortUrl,"is",db.fetchActual(shortUrl)[0])
                    db.incrementUrlCount(session['username'])
                    return render_template("shrturl.html", url=shortUrl)
            else:
                msg = "Enter valid URL"
                return  render_template("index.html", msg=msg)

        else:
            return render_template("index.html")
    else:
        return "404 Not Found"

@app.route('/')
@app.route('/login', methods =['GET', 'POST'])
def login():
    db = dbcurd()
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        account = db.userLogin(username,password)
        # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # cursor.execute('SELECT * FROM accounts WHERE username = % s AND password = % s', (username, password, ))
        # account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account[0]
            session['username'] = account[1]
            msg = 'Logged in successfully !'
            return render_template('index.html', msg = msg)
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg = msg)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))
  
@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    db = dbcurd()
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        account = db.fetchclone(username)
        # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # cursor.execute('SELECT * FROM accounts WHERE username = % s', (username, ))
        # account = cursor.fetchclone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password or not email:
            msg = 'Please fill out the form !'
        else:
            state = db.userRegister(username,password,email)
            # cursor.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s)', (username, password, email, ))
            # mysql.connection.commit()
            if(state):
                msg = 'You have successfully registered !'
            else:
                msg = 'Not able to register!'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg = msg)


@app.route('/<string:url>',methods=['GET'])
def Redirect(url):
    db = dbcurd()
    print(url)
    shortUrl = "http://127.0.0.1:5000/"+url 
    try:
        actualUrl = str(db.fetchActual(shortUrl)[0])
    except:
        return  ("http://127.0.0.1:5000/"+url+" is Not found")
    else:
        db.updateHitCount(actualUrl)
        return redirect(actualUrl)
    

if __name__ == "__main__":
    app.run(debug=True)