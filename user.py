import mysql.connector
from flask import session
import hashlib
from datetime import datetime

import pymysql
pymysql.install_as_MySQLdb()
import MySQLdb



class user_operation:
     
    def myconnection(self):
        try:
            conn = MySQLdb.connect(host="localhost",
                           user = "root",
                           passwd = "",
                           port=3306,
                           db = "rideon")

            
            return conn

        except Error as e:
            # Catch any exception and print the error message
            print(f"Error connecting to MySQL: {e}")
            return None

        finally:
            print("error")
            # Optional: Add any cleanup logic here (if needed)
            pass
#------------------------------------------------------------------------------------------------------------------
    def user_signup_insert(self,name,email,mobile,password):
        con=self.myconnection()
        sq="insert into user(name,email,mobile,password) values(%s,%s,%s,%s)"
        record = [name,email,mobile,password]
        cursor=con.cursor()  
        cursor.execute(sq, record)
        con.commit()
        cursor.close()
        con.close()
        return
#-----------------------------------------------------------------------------------------------------------------------
    def user_delete(self,email):
        con=self.myconnection()
        sq="delete from user where email=%s"
        record = [email]
        cursor=con.cursor()  
        cursor.execute(sq, record)
        con.commit()
        cursor.close()
        con.close()
        return
#------------------------------------------------------------------------------------------------------------------------
    def user_login_verify(self,email,password):
        print("Connection Start")
        con=self.myconnection()
        print("Connection sucess")
        sq="select name,email from user where email=%s and password=%s"
        pas = hashlib.md5(password.encode())
        password = pas.hexdigest()
        record = [email,password]
        cursor=con.cursor()  
        cursor.execute(sq, record)
        row = cursor.fetchall()
        rc = cursor.rowcount
        cursor.close()
        con.close()
        if rc == 0:
           return 0
        else:
           for r in row:
               session['user_name'] = r[0]
               session['user_email'] = r[1]  
           return 1

#-----------------------------------------------------------------------------------------------------------------------------        
    def user_profile(self):
        con=self.myconnection()
        sq="select name,email,mobile from user where email=%s"
        record = [session['user_email']]
        cursor=con.cursor()  
        cursor.execute(sq, record)
        row = cursor.fetchall()
        return row  
#-------------------------------------------------------------------------------------------------------------------------------
    def user_profile_update(self,name,mobile):
        con=self.myconnection()
        sq="update user set name=%s,mobile=%s where email=%s"
        record = [name,mobile,session['user_email']]
        cursor=con.cursor()  
        cursor.execute(sq, record)
        con.commit()
        cursor.close()
        con.close()
        return 

#--------------------------------------------------------------------------------------------------------------------------------
    def user_bike_search(self,city):
        con=self.myconnection()
        sq="SELECT b.photo, b.model_name, b.reg_no, b.charge, b.mfg_date, b.descp, b.bike_id, p.provider_id FROM bike b JOIN provider p ON b.provider_id = p.provider_id WHERE p.city = %s"
        record = [city]
        cursor=con.cursor()
        cursor.execute(sq,record)
        row = cursor.fetchall()
        return row 

#-------------------------------------------------------------------------------------------------------------------------------------
    def user_bike_date_insert(self,bike_id,provider_id,start_date,end_date,charges):
        con=self.myconnection()
        check_query = """
                        SELECT COUNT(*) FROM rent 
                        WHERE bike_id = %s 
                        AND (
                            (start_date <= %s AND end_date >= %s) 
                            OR 
                            (start_date <= %s AND end_date >= %s) 
                            OR 
                            (start_date >= %s AND end_date <= %s)
                        );
                        """
        cursor=con.cursor()
        cursor.execute(check_query, (bike_id, start_date, start_date, end_date, end_date, start_date, end_date))
        result = cursor.fetchone()
        if result[0] == 0:

            sq="insert into rent(user_email,bike_id,provider_id,start_date,end_date,charges) values(%s,%s,%s,%s,%s,%s)"
            start_date = datetime.strptime(start_date,'%Y-%m-%d')
            end_date = datetime.strptime(end_date,'%Y-%m-%d')
            total_day = end_date-start_date
            total_day = total_day.days        #  return number of days
            charges = int(charges)*total_day
            record = [session['user_email'],bike_id,provider_id,start_date,end_date,charges]

            cursor=con.cursor()  
            cursor.execute(sq, record)
            con.commit()
            cursor.close()
            con.close()
            return  "Bike booking is confirm!!!"
        else:
            return  "Bike Not Avilable  Selected Date"
#----------------------------------------------------------------------------------------------------------------------------------------  
    def user_rent_view(self):
        con=self.myconnection()
        sq="select rent_id,reg_no,model_name,descp,start_date,end_date,charges,photo from rent r,bike b where r.bike_id=b.bike_id and user_email=%s"
        record = [session['user_email']]
        cursor = con.cursor()
        cursor.execute(sq,record)
        row = cursor.fetchall()
        return row
#---------------------------------------------------------------------------------------------------------------------------------------
    def user_rent_view_admin(self):
        con=self.myconnection()
        sq="select rent_id,reg_no,model_name,descp,start_date,end_date,charges,photo from rent r,bike b where r.bike_id=b.bike_id "
       
        cursor = con.cursor()
        cursor.execute(sq)
        row = cursor.fetchall()
        return row
    
    
    def user_review(self,bike_id):
        con=self.myconnection()
        sq="select star,name,message from review r, user u where r.user_email=u.email and bike_id=%s"
        
        record = [bike_id]
        cursor=con.cursor()  
        cursor.execute(sq,record)
        row = cursor.fetchall()
        return row 
        
#------------------------------------------------------------------------------------------------------------------------------------------
    def user_review_insert(self,bike_id,star,message):
        con=self.myconnection()
        sq="insert into review(user_email,bike_id,star,message) values(%s,%s,%s,%s)"
        record = [session['user_email'],bike_id,star,message]
        cursor=con.cursor()  
        cursor.execute(sq,record)
        con.commit()
        cursor.close()
        con.close()
        return
#------------------------------------------------------------------------------------------------------------------------------------------
