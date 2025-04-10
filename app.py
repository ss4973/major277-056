from flask import Flask, redirect, render_template,request,flash, request_started,url_for,session

from user import user_operation
from provider import provider_operation
from captcha.image import ImageCaptcha
import random
import hashlib
from datetime import datetime
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler
import joblib


scaler_filename = "scaler.save"

scaler = joblib.load(scaler_filename)
print("Scaler loaded successfully.")

# Load the model
model = load_model('lstm_model.h5')
print("Model loaded successfully.")
model.summary()

app = Flask(__name__)

app.secret_key = "hkldsjfklds78784hdsy787i"
#-------------------mail configuration---------------------------


#----------------------------------------------------------

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    return render_template('admin_dashboard.html')


#------------------user sign up pages--------------------------------------------------
@app.route('/user_signup')
def user_signup():
    num=random.randrange(1000,9999)
    # Create an image instance of the given size
    imgpython = ImageCaptcha(width = 280, height = 90)

    # Image captcha text
    global captcha_text
    captcha_text = str(num)
 
    # write the image on the given file and save it
    img.write(captcha_text, 'static/images/CAPTCHA.png')
    return render_template('user_signup.html')
#-------------------------------------------------------------------------------------------
@app.route('/user_signup_insert',methods=['GET','POST'])
def user_signup_insert():
    if request.method=='POST': 
        if captcha_text!=request.form["captcha"]:
                        flash("invalid captcha!!!")
                        return render_template('user_signup.html')

        name=request.form["name"]
        email=request.form["email"]
        mobile=request.form["mobile"]
        password=request.form["password"]
        #--- password hashing----------------
        pas = hashlib.md5(password.encode())
        password = pas.hexdigest()
        #---------user insert-----------------
        op = user_operation()  # object create
        op.user_signup_insert(name,email,mobile,password)
     
        global otp
        otp = random.randint(100000,999999)
      
        return redirect(url_for('user_signup'))


#------------------user login pages--------------------------------------------------
@app.route('/user_login')
def user_login():
    return render_template('user_login.html')
#----------------- User Login Verify -------------------------------------------------
@app.route('/user_login_verify',methods=['GET','POST'])
def user_login_verify():
    if request.method=='POST':
        email=request.form['email']
        password=request.form['password']
        op = user_operation()
        print(email)
        print(password)
        r=op.user_login_verify(email,password)
        print(r)
        if r==0:
            flash("Invalid Email or Password")
            return redirect(url_for('user_login'))
        else:
            return redirect(url_for('user_dashboard'))

#------------- User LogOut----------------------------------------------------
@app.route('/user_logout')
def user_logout():
    session.clear()
    return redirect(url_for('user_login'))

@app.route('/admin_logout')
def admin_logout():
     return render_template('index.html')

#------------------------------------------------------------------------------

#------------- User Dashboard -----------------------------------------------
@app.route('/user_dashboard')
def user_dashboard():
    if 'user_email' in session:
        return render_template('user_dashboard.html')
    else:
        flash("you are not logged in .. login now!!!")
        return redirect(url_for('user_login'))

#---------------- User Profile -----------------------------------------------
@app.route('/user_profile')
def user_profile():
    if 'user_email' in session:
        op = user_operation()
        r=op.user_profile()
        return render_template('user_profile.html',rec=r)
    else:
        flash("you are not logged in .. login now!!!")
        return redirect(url_for('user_login'))


#-------------- User Profile Update -------------------------------------------------
@app.route('/user_profile_update',methods=['GET','POST'])
def user_profile_update():
    if 'user_email' in session:
        if request.method=='POST':
            name=request.form['name']
            mobile=request.form['mobile']
            op = user_operation()
            op.user_profile_update(name,mobile)
            flash("your profile is updated successfully!!!")
            return redirect(url_for('user_profile'))
    else:
        flash("you are not logged in .. login now!!!")
        return redirect(url_for('user_login'))


#--------------- User Bike ------------------------------------------------------------
@app.route('/user_bike')
def user_bike():
    if 'user_email' in session:
        return render_template('user_bike.html')
    else:
        flash("you are not logged in .. login now!!!")
        return redirect(url_for('user_login'))
#--------------------------------------------------------------------------------------
@app.route('/user_bike_search',methods=['GET','POST'])
def user_bike_search():
    if 'user_email' in session:
        if request.method=='POST':
            city=request.form['city']
            op = user_operation()
            r=op.user_bike_search(city)
            rent_prices = [bike[3] for bike in r]
            preesult=[]
            for i in  rent_prices:
                new_data = np.array([[i]])  # Replace 'your_value' with the actual data point

                # Scale the new data point using the loaded scaler
                scaled_data = scaler.transform(new_data)

                # Prepare the data for the LSTM model (time_step should be the same as in training)
                time_step = 15
                if len(scaled_data) < time_step:
                    padded_data = np.zeros((time_step, 1))
                    padded_data[-len(scaled_data):] = scaled_data
                else:
                    padded_data = scaled_data[-time_step:]

                X_single = padded_data.reshape(1, time_step, 1)

                # Predict the value for the single data point
                predicted_value = model.predict(X_single)
                predicted_value = scaler.inverse_transform(predicted_value)  # Inverse scale to get actual value
                print("Predicted value:", predicted_value[0][0])
                preesult.append(predicted_value[0][0])
            print(preesult)
            return render_template('user_bike.html',rec=r,predicted=preesult)
    else:
        flash("you are not logged in .. login now!!!")
        return redirect(url_for('user_login'))


#-----------------User Bike Date-------------------------------------------------------
@app.route('/user_bike_date',methods=['GET','POST'])
def user_bike_date():
    if 'user_email' in session:
        if request.method=='GET':
            bike_id=request.args.get('bike_id')
            provider_id=request.args.get('provider_id')
            charges=request.args.get('charges')
            return render_template('user_bike_date.html',bike_id=bike_id,provider_id=provider_id,charges=charges)
    else:
        flash("you are not logged in .. login now!!!")
        return redirect(url_for('user_login'))

#---------------------User Bike Date Insert--------------------------------------------
@app.route('/user_bike_date_insert',methods=['GET','POST'])
def user_bike_date_insert():
    if 'user_email' in session:
        
        if request.method=='POST':
            bike_id=request.form['bike_id']
            provider_id=request.form['provider_id']
            start_date=request.form['start_date']
            end_date=request.form['end_date']
            charges=request.form['charges']
            op = user_operation()
            message=op.user_bike_date_insert(bike_id,provider_id,start_date,end_date,charges)

            flash(message)
            return redirect(url_for('user_dashboard'))
    else:
        flash("you are not logged in .. login now!!!")
        return redirect(url_for('user_login'))
#---------------------------------------------------------------------------------------
@app.route('/user_rent_view')
def user_rent_view():
    if 'user_email' in session:
        op = user_operation()
        r=op.user_rent_view()
        return render_template('user_rent_view.html',rec=r)
    else:
        flash("you are not logged in .. login now!!!")
        return redirect(url_for('user_login'))

@app.route('/admin_user_rent_view')
def admin_user_rent_view():
   
        op = user_operation()
        r=op.user_rent_view_admin()
        return render_template('admin_user_rent_view.html',rec=r)
   
#-----------------------------------------------------------------------------------------------
@app.route('/user_review',methods=['GET','POST'])
def user_review():
    if 'user_email' in session:
        if request.method == 'GET':
            bike_id=request.args.get('bike_id')
            op = user_operation()
            r=op.user_review(bike_id)
            return render_template('user_review.html',rec=r,bike_id=bike_id)
    else:
        flash("you are not logged in .. login now!!!")
        return redirect(url_for('user_login'))

#-------------------------------------------------------------------------------------------------
@app.route('/user_review_insert',methods=['GET','POST'])
def user_review_insert():
    if 'user_email' in session:
        if request.method=='POST':
            bike_id=request.args.get('bike_id')
            star=request.form['star']
            message=request.form['message']
            op = user_operation()
            op.user_review_insert(bike_id,star,message)
            flash("Your review is submitted successfully!")
            return redirect(url_for('user_review',bike_id=bike_id))
    else:
        flash("you are not logged in .. login now!!!")
        return redirect(url_for('user_login'))


#--------------------------------------------------------------------------------------
#------------------------------- provider routing--------------------------------------
#--------------------------------------------------------------------------------------
@app.route('/provider_signup')
def provider_signup():
    num=random.randrange(1000,9999)
    # Create an image instance of the given size
    img = ImageCaptcha(width = 280, height = 90)

    # Image captcha text
    global captcha_text1
    captcha_text1 = str(num)
 
    # write the image on the given file and save it
    img.write(captcha_text1, 'static/images/CAPTCHA1.png')
    return render_template('provider_signup.html')
#---------------------------------------------------------------------------------------
@app.route('/provider_signup_insert',methods=['GET','POST'])
def provider_signup_insert():
    if request.method=='POST': 
        if captcha_text1!=request.form["captcha"]:
                        flash("invalid captcha!!!")
                        return render_template('provider_signup.html')

        name=request.form["name"]
        email=request.form["email"]
        mobile=request.form["mobile"]
        address=request.form["address"]
        city=request.form["city"]
        password=request.form["password"]
        #--- password hashing----------------
        pas = hashlib.md5(password.encode())
        password = pas.hexdigest()
        #---------provider insert-----------------
        op = provider_operation()  # object create
        rec=op.provider_signup_insert(name,email,mobile,address,city,password)
        for r in rec:
            flash("Your Provider ID is: "+ str(r[0])+"  ..... login now..")
        return render_template('provider_login.html')
#----------------------------------------------------------------------------------------
#------------------provider login pages--------------------------------------------------
@app.route('/provider_login')
def provider_login():
    return render_template('provider_login.html')
#-----------------------------------------------------------------------------------------
@app.route('/provider_login_verify',methods=['GET','POST'])
def provider_login_verify():
    if request.method=='POST':
        provider_id=request.form['provider_id']
        password=request.form['password']
        op = provider_operation()
        r=op.provider_login_verify(provider_id,password)
        if r==0:
            flash("Invalid ID or Password")
            return redirect(url_for('provider_login'))
        else:
            return redirect(url_for('provider_dashboard'))

#------------------------------------------------------------------------------------------
@app.route('/provider_logout')
def provider_logout():
    session.clear()
    return redirect(url_for('provider_login'))
#------------------------------------------------------------------------------------------
@app.route('/provider_dashboard')
def provider_dashboard():
    if 'provider_id' in session:
        return render_template('provider_dashboard.html')
    else:
        flash("you are not logged in .. login now!!!")
        return redirect(url_for('provider_login'))
#--------------------------------------------------------------------------------------------
@app.route('/provider_profile')
def provider_profile():
    if 'provider_id' in session:
        op = provider_operation()
        r=op.provider_profile()
        return render_template('provider_profile.html',rec=r)
    else:
        flash("you are not logged in .. login now!!!")
        return redirect(url_for('provider_login'))
#--------------------------------------------------------------------------------------------------
@app.route('/provider_profile_update',methods=['GET','POST'])
def provider_profile_update():
    if 'provider_id' in session:
        if request.method=='POST':
            email=request.form['email']
            mobile=request.form['mobile']
            address=request.form['address']
            op = provider_operation()
            op.provider_profile_update(email,mobile,address)
            flash("your profile is updated successfully!!!")
            return redirect(url_for('provider_profile'))
    else:
        flash("you are not logged in .. login now!!!")
        return redirect(url_for('provider_login'))

#-----------------------------------------------------------------------------------------------------
@app.route('/provider_bike')
def provider_bike():
    if 'provider_id' in session:
        return render_template('provider_bike.html')
    else:
        flash("you are not logged in .. login now!!!")
        return redirect(url_for('provider_login'))

#-------------------------------------------------------------------------------------------------------
@app.route('/provider_bike_insert',methods=['GET','POST'])
def provider_bike_insert():
    if 'provider_id' in session:
        if request.method=='POST':
            model_name=request.form['model_name']
            reg_no=request.form['reg_no']
            charge=request.form['charge']
            mfg_date=request.form['mfg_date']
            descp=request.form['descp']
            # for photo upload
            photo=request.files["photo"]
            photo_name = photo.filename
            photo.save("static/bike/" + photo_name)
            #----bike insert-------------------
            op = provider_operation()
            op.provider_bike_insert(model_name,reg_no,charge,mfg_date,descp,photo_name)
            flash("your bike is inserted successfully!!!")
            return redirect(url_for('provider_bike'))
    else:
        flash("you are not logged in .. login now!!!")
        return redirect(url_for('provider_login'))
#-------------------------------------------------------------------------------------------------------------
@app.route('/provider_bike_view')
def provider_bike_view():
    if 'provider_id' in session:
        op = provider_operation()
        r=op.provider_bike_view()
        return render_template('provider_bike_view.html',rec=r)
    else:
        flash("you are not logged in .. login now!!!")
        return redirect(url_for('provider_login'))
@app.route('/admin_provider_bike_view')
def admin_provider_bike_view():
   
        op = provider_operation()
        r=op.admin_provider_bike_view()
        return render_template('admin_provider_bike_view.html',rec=r)
  
#----------------------------------------------------------------------------------------------------------------
@app.route('/provider_bike_delete',methods=['GET','POST'])
def provider_bike_delete():
    if 'provider_id' in session:
        if request.method=='GET':
            bike_id=request.args.get('bike_id')
            op = provider_operation()
            op.provider_bike_delete(bike_id)
            flash("bike is deleted successfully!!!")
            return redirect(url_for('provider_bike_view'))
    else:
        flash("you are not logged in .. login now!!!")
        return redirect(url_for('provider_login'))

#----------------------------------------------------------------------------------------------------------------------
@app.route('/provider_bike_profile',methods=['GET','POST'])
def provider_bike_profile():
    if 'provider_id' in session:
        if request.method=='GET':
            bike_id=request.args.get('bike_id')
            op = provider_operation()
            r=op.provider_bike_profile(bike_id)
            return render_template ('provider_bike_profile.html',rec=r)
    else:
        flash("you are not logged in .. login now!!!")
        return redirect(url_for('provider_login'))

#------------------------------------------------------------------------------------------------------------------------
@app.route('/provider_bike_profile_update',methods=['GET','POST'])
def provider_bike_profile_update():
    if 'provider_id' in session:
        if request.method=='POST':
            bike_id=request.args.get('bike_id')
            model_name=request.form['model_name']
            reg_no=request.form['reg_no']
            charge=request.form['charge']
            mfg_date=request.form['mfg_date']
            descp=request.form['descp']
            op = provider_operation()
            op.provider_bike_profile_update(bike_id,model_name,reg_no,charge,mfg_date,descp)
            flash("Your Bike Details are Updated successfully!!!")
            return redirect(url_for('provider_bike_profile',bike_id=bike_id))
    else:
        flash("you are not logged in .. login now!!!")
        return redirect(url_for('provider_login'))
#--------------------------------------------------------------------------------------------------------------------------------
@app.route('/provider_bike_rent')
def provider_bike_rent():
    if 'provider_id' in session:
        op = provider_operation()
        r=op.provider_bike_rent()
        return render_template('provider_bike_rent.html',rec=r)
    else:
        flash("you are not logged in .. login now!!!")
        return redirect(url_for('provider_login'))
#-----------------------------------------------------------------------------------------------------------------------------
@app.route('/provider_delete')
def provider_delete():
    if 'provider_id' in session:
        op = provider_operation()
        r=op.provider_delete()
        flash("you account is deleted successfully..join with us!")
        return redirect(url_for('provider_signup'))
    else:
        flash("you are not logged in .. login now!!!")
        return redirect(url_for('provider_login'))


@app.route('/manifest.json')
def manifest():
    return app.send_static_file('manifest.json')

if __name__=="__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
