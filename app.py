from flask import Flask,render_template,request,flash,redirect,url_for,session,logging




from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from passlib.hash import sha256_crypt
from functools import wraps

import pickle , numpy as np


app = Flask(__name__)
model1 = pickle.load(open('/home/mohamed/BusinessForcaster/xgb_test.pickle', 'rb'))



#config MySQL

app.config['MYSQL_HOST'] ='localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] ='191997'
app.config['MYSQL_DB'] = 'myflaskapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor' # cursor return tuple per default, we specify dict

#initialize MySQL

mysql = MySQL(app)



#Articles = Articles()
def required_login(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if 'logged_in' not in session:
            flash("Unauthorized, please login ",'danger')
            return redirect(url_for('login'))
        return f(*args,**kwargs)
    return wrap


def required_not_logged_in(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if 'logged_in' in session:
            flash("Unauthorized",'danger')
            return redirect(url_for('index'))
        return f(*args,**kwargs)
    return wrap




@app.route('/')
def index():
    return render_template('Home.htm')

@app.route('/About')
def about():
    return render_template('About.htm')


@app.route('/Articles')
def articles():

    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * from articles")
    if result>0 : 
        articles = cur.fetchall()
        return render_template('Articles.htm',articles=articles)
    else:
        msg = "no articles available"
        return render_template('Articles.htm',msg=msg)
    cur.close()  

    return render_template('Articles.htm',articles = articles) 



@app.route('/Articles/<string:id>/')
def article(id):
   
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * from articles WHERE id=%s",[id])
    if result>0 :
        article=cur.fetchone()
        return render_template('Article.htm',article=article)
    else:
        flash("article not available",'danger')
    cur.close()
    return redirect(url_for('articles'))


class RegisterForm(Form):
    name = StringField('Name',validators=[validators.Length(min=1,max=50)])
    username=StringField('Username',validators=[validators.Length(min=4,max=25)])
    email = StringField('Email',[validators.Length(min=6,max=50)])
    password=PasswordField('Password',[
        validators.DataRequired() ,
        validators.EqualTo('confirm',message="passwords do not match")])
    confirm=PasswordField('Confirm password')


@app.route('/register',methods=['GET','POST']) #route accepts get request per default but we precise here post also
@required_not_logged_in
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate(): # check if form is validated and its a post request
        #getting data using wtforms
        name = form.name.data
        email = form.email.data
        username= form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))
      
        #create cursor

        cur =mysql.connection.cursor()

        # execute SQL command

        cur.execute("INSERT INTO users(name,email,username,password) VALUES (%s,%s,%s,%s)",(name,email,username,password) )
    
        #commit to DB 

        mysql.connection.commit()


        #close connection

        cur.close()
        flash("registrated successfuly" , "success") #first field :message, second:category
        return redirect(url_for('login'))

    return render_template('register.htm',form=form)



@app.route('/login',methods=['GET','POST'])
@required_not_logged_in
def login():

    if request.method == 'POST' :

        username = request.form.get("username", False)
        password_candidate = request.form['password']
        
       
        cur = mysql.connection.cursor()
        result = cur.execute(" SELECT * FROM users WHERE username = %s",[username])
        
        if result>0 :
            data = cur.fetchone()  # dictionnary returned as configured above ( returns tuple if not configured)
            password = data['password']        

            if  sha256_crypt.verify(password_candidate,password) :
                session['logged_in']=True  #save user is logged in 
                session['username']=username   #to save username
                flash('you are now logged in' ,'success')
                return redirect(url_for('forecast'))
            else:
                error= "Invalid login"
               # app.logger.info("login no ")
                return render_template('login.htm',error=error)
            cur.close()
        else:
            error= "Username not found"
            #app.logger.info("username no")
            return render_template('login.htm',error=error)

    return render_template('login.htm') 





@app.route('/logout')
@required_login
def logout():
    session.clear()
    flash("you are now logged out","success")
    return redirect(url_for('login'))




@app.route('/forecast',methods=['GET','POST'])
@required_login
def forecast():
    if request.method == 'POST' : 

        int_features = [int(x) for x in request.form.values()]
        

        int_features.insert(0,34)   #adding date block at the beginning
        
        final_features = [np.array(int_features)]
        
        item_price = model.predict(final_features)
        
           
        #int_features.append(item_price[0]) #adding item price to features
       
        final_features = [np.array(int_features)]
        preds = model.predict(final_features)
        
        output = round(preds[0],2)
        session['test']=True          # to show message only when post method is done 

        return render_template('Forecast.htm',output = output)
       

    return render_template('Forecast.htm')

    

if __name__ =='__main__':
    app.secret_key='secret123'
    app.run(debug=True)
