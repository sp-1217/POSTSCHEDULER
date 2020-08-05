from flask import Flask, render_template, flash, redirect, url_for,session,request, logging,g
#from data import Articles
from flask_sqlalchemy import SQLAlchemy 
from datetime import datetime
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
from flask_sendgrid import SendGrid
import os
from celery import Celery
from datetime import datetime
from flask_celery import make_celery 
#my_cron = CronTab(user='surbhi')
from dateutil import tz
from twilio.rest import Client
import arrow
# skipped your comments for readability
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests
#client = nexmo.Client(key='6539724f', secret='S3aEhM2BhLcRJlAX')


#secret_key=guess it
#for database sqlite3 sqlalchemy ORM
#create a database
#connect to a database
#make a table in the database
#->pip3 install apt-get sqlite3
#->sqlite3 exampl.db
#->.tables
#->exit()

app = Flask(__name__,template_folder='templates')
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example4.db'##folder destination where db is stored
app.secret_key = os.urandom(24)
db = SQLAlchemy(app)

app.config['CELERY_BROKER_URL']='redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND']='redis://localhost:6379/0'

celery=make_celery(app)



#name
#phone no.
#email
#usename
#password
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    phoneno= db.Column(db.String(50), nullable=False)
    email= db.Column(db.String(50), nullable=False)
    Username = db.Column(db.String(50), nullable=False)
    Password = db.Column(db.String(50), nullable=False)
    messages=db.relationship('Mesaage',backref='owner')

class Mesaage(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    sub=db.Column(db.String(50))
    body=db.Column(db.String(50))
    to=db.Column(db.String(50))
    frm=db.Column(db.String(50))
    status=db.Column(db.String(50))
    typee=db.Column(db.String(50))
    date=db.Column(db.Integer)
    time=db.Column(db.Integer)
    owner_id=db.Column(db.Integer,db.ForeignKey('user.id'))


@celery.task(name='app.my_background_task')
def my_background_task(sob):
    # Download the helper library from https://www.twilio.com/docs/python/install
    


    # Your Account Sid and Auth Token from twilio.com/console
    # DANGER! This is insecure. See http://twil.io/secure
    post = Mesaage.query.filter_by(id=sob).one()
    st=''
    st='http://localhost:5000/update/'+str(sob)
    r=requests.put(st)

    account_sid = 'ACe73815a23add251648b4fb888fbb9ec5'
    auth_token = '34f3ab38167488e203831546f4a54a93'
    client = Client(account_sid, auth_token)

    

    message = client.messages \
            .create(
                    body=post.body,
                     from_='+15054046917',
                     to='+919661287011'
               )

    


    #with open('please.txt','a') as outFile:
        #outFile.write('\n' + message.sid )
    

@celery.task(name='app.mail_send')
def mail_send(sob):
    print(sob)
    me = "surbhip1217@gmail.com"
    my_password = r"attentionnottension"
    you = "surbhip121719@gmail.com"

    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Alert"
    msg['From'] = me
    msg['To'] = you
    result = Mesaage.query.filter_by(id=sob).one()

    body=result.body
    part2 = MIMEText(body, 'plain')

    msg.attach(part2)



# Send the message via gmail's regular server, over SSL - passwords are being sent, afterall
    s = smtplib.SMTP_SSL('smtp.gmail.com')
# uncomment if interested in the actual smtp conversation
# s.set_debuglevel(1)
# do the smtp auth; sends ehlo if it hasn't been sent already
    s.login(me, my_password)
           
    s.sendmail(me, you, msg.as_string())
    st='http://localhost:5000/update/'+str(sob)
    r=requests.put(st)

    s.quit()




    
@app.route('/update/<int:id>',methods=['PUT'])
def update(id):
     post = Mesaage.query.filter_by(id=id).one()
     post.status='1'
     db.session.commit()
     return redirect(url_for('home'))



@app.route('/',methods=['GET'])
def add():
    #r=requests.put('http://127.0.0.1:5000/update/2')
    #print(r.status_code)
    return render_template('home.html')



@app.route('/list',methods=['GET'])
def list():
    posts = Mesaage.query.order_by(Mesaage.date.desc()).all()
    return render_template('list.html',post=posts)


#pagination
@app.route('/thread/<int:page_num>')
def thred(page_num):
    threads=Mesaage.query.order_by(Mesaage.date.desc()).paginate(per_page=10,page=page_num,
    error_out=True)
    if g.user:
        return render_template('list.html',post=threads)
    return redirect(url_for('login'))
   
    

@app.route('/delete/<string:id>')
def dele(id):
    post = Mesaage.query.filter_by(id=id).one()
    db.session.delete(post)
    db.session.commit()
    return redirect('/thread/1');


@app.route('/detail/<int:id>',methods=['GET'])
def detail(id):
    message=Mesaage.query.filter_by(id=id).one()
    if g.user:
        return render_template('details.html',message=message)
    return redirect(url_for('login'))
    


@app.route('/signup',methods=['POST','GET'])
def signup():
    if request.method == 'POST':
	
        name = request.form['name']
        phoneno = request.form['phoneno']
        email = request.form['email']
        username= request.form['Username']
        password=sha256_crypt.encrypt(request.form['Password'])
    

        post = User(name=name, phoneno=phoneno, email=email, Username=username, Password=password)

        db.session.add(post)
        db.session.commit()
    #return '<h1>T:{} P:{} E:{} U:{} Pa:{}</h1>'.format(name,phoneno,email,username,password)
        return redirect(url_for('add'))
    else:
        return render_template('signup.html')


# User login
@app.route('/login', methods=['GET'])
def login():
	return render_template('login.html')

@app.route('/home',methods=['GET'])
def home():
	return render_template('home.html')




# Logout
@app.route('/logout')
#@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))
#session implemetation not done


@app.route('/logins',methods=['POST'])
def logins():
    # Get Form Fields
    username = request.form['username']
    password_candidate = request.form['password']
    #console.log(username);

        # Create cursor
        #cur = mysql.connection.cursor()

        # Get user by username
        #result = cur.execute("SELECT * FROM users WHERE username = %s", [username])
    result = User.query.filter_by(Username=username).one()
    
    #console.log(result)
    print(result)
    if result :
            # Get stored hash
        
        #print(data)
        password = result.Password
        session.pop('user', None)
            # Compare Passwords
        if sha256_crypt.verify(password_candidate, password):
                # Passed
           #session['logg0ed_in'] = True
           #session['username'] = username
            session['logged_in']=True;
            session['user'] = request.form['username']
            return redirect(url_for('home'))
        else:
            return redirect(url_for('login'))
           
    else:
        return redirect(url_for('login'))#error


@app.before_request
def before_request():
    g.user = None
    if 'user' in session:
        g.user = session['user']

@app.route('/message',methods=['GET','POST'])
def index():
    if request.method == 'POST':

        subject = request.form['sub']
        body = request.form['body']
        to = request.form['to']
        frm= '+15054046917'
        status='0'
        typee='sms'
        date=request.form['date']
        time=request.form['time']
        se=User.query.filter_by(Username=g.user).first()

        poste = Mesaage(sub=subject,body=body,status=status,typee=typee, to=to, frm=frm, date=date,time=time,owner=se)

        db.session.add(poste)
        db.session.commit()
        #post= Mesaage.query.filter_by(time=time).one()
        x=int(date[:4]);
        y=int(date[5:7]);

        z=int(date[8:10]);
        m=int(time[:2]);
        n=int(time[3:5]);
        print(poste.id)
        #lu=Mesaage.query.filter_by(body=body).one()
        my_background_task.apply_async(args=[poste.id],eta=arrow.get(datetime(x, y, z,hour=m,minute=n,second=0), tz.gettz('Asia/Kolkata')).to('utc').naive)
        #my_background_task.apply_async(countdown=60)
    #return '<h1>T:{} P:{} E:{} U:{} Pa:{}</h1>'.format(name,phoneno,email,username,password)
        return redirect(url_for('home'))
    
        #eta=#datetime(2019,6,11,hour=13,minute=17,second=0))
        #schedule.every().sunday.at("16:17").do(
        #schedule.every().minute.do(job_that_executes_once)#,request.form['number'],request.form['message'])
           
    else:
        if g.user:
            return render_template('message.html')
        return redirect(url_for('login'))


@app.route('/formail',methods=['GET','POST'])
def formm():
    if request.method == 'POST':
        subject = request.form['sub']
        body = request.form['body']
        to = request.form['to']
        frm= 'surbhip1217@gmail.com'
        date=request.form['date']
        time=request.form['time']
        status='0'
        typee='mail'
        se=User.query.filter_by(Username=g.user).first()

        poste = Mesaage(sub=subject,body=body, status=status,typee=typee,to=to, frm=frm, date=date,time=time,owner=se)

        db.session.add(poste)
        db.session.commit()
        
        x=int(date[:4]);
        y=int(date[5:7]);

        z=int(date[8:10]);
        m=int(time[:2]);
        n=int(time[3:5]);
        print('Ihave come')
        print(poste.id)
        #lu=Mesaage.query.filter_by(body=body).one()
        mail_send.apply_async(args=[poste.id],eta=arrow.get(datetime(x, y, z,hour=m,minute=n,second=0), tz.gettz('Asia/Kolkata')).to('utc').naive)
        #my_background_task.apply_async(countdown=60)
    #return '<h1>T:{} P:{} E:{} U:{} Pa:{}</h1>'.format(name,phoneno,email,username,password)
        return redirect(url_for('home'))
    
        #eta=#datetime(2019,6,11,hour=13,minute=17,second=0))
        #schedule.every().sunday.at("16:17").do(
        #schedule.every().minute.do(job_that_executes_once)#,request.form['number'],request.form['message'])
           
    else:
        if g.user:
            return render_template('formmail.html')
        return redirect(url_for('login'))

@app.route('/getsession')
def getsession():
    if 'user' in session:
        return session['user']

    return 'Not logged in!'

@app.route('/dropsession')
def dropsession():
    session.pop('user', None)
    return 'Dropped!'

if __name__ == '__main__':
    app.run(debug=True) 
