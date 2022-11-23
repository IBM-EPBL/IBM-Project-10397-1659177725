import numpy as np
import os
from flask import Flask, request, jsonify, render_template,json,redirect,url_for,flash
import pickle
import requests
import sqlite3

# NOTE: you must manually set API_KEY below using information retrieved from your IBM Cloud account.
API_KEY = "PMs8xiWIKSLPj0wve8skInojd34H_qHwqlOc4PeFPzB2"
token_response = requests.post('https://iam.cloud.ibm.com/identity/token', data={"apikey":
 API_KEY, "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'})
mltoken = token_response.json()["access_token"]

header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + mltoken}

app = Flask(__name__)
app.secret_key="21433253"
conn=sqlite3.connect("database1.db")
conn.execute("CREATE TABLE IF NOT EXISTS login(email TEXT PRIMARY KEY,password TEXT)")
conn.close()

@app.route('/')
def main():
    return render_template('login.html')

@app.route('/login',methods=['POST','GET'])
def login():
    if request.method=='POST':
        try:
            print("request1")
            fv=[x for x in request.form.values()]
            print(fv)
            print([x for x in request.form.values()])
            print(request.form["email"])
            email=request.form["email"]
            pswd=request.form["pswd"]
            print("request2")
            conn=sqlite3.connect("database1.db")
            cur=conn.cursor()
            print(email,pswd)
            cur.execute("SELECT password FROM login WHERE email=?;",(str(email),))
            print("select")
            
            result=cur.fetchone()
            cur.execute("SELECT * FROM login")
            print(cur.fetchall())
            print("fetch")
            if result:
                print("login successfully success")
                print(result)
                if result[0]==pswd:
                    flash("login successfully",'success')
                    return redirect('/home')
                else:
                    return render_template("login.html", error="please enter correct password")
                
            else:
                print("register")
                flash("please Register",'danger')
                
                return redirect('/reg')
            
        except Exception as e:
            print(e)
            print('danger-----------------------------------------------------------------')
            return "hello error" 
    else:
        return render_template("login.html")
#    return render_template('login.html')
@app.route('/reg')
def reg():
    return render_template("register.html")

@app.route('/register',methods=['POST','GET'])
def register():
    if request.method=='POST':
        try:
            print("request1")
            fv=[x for x in request.form.values()]
            print(fv)
            print([x for x in request.form.values()])
            print(request.form["email"])
            email=request.form["email"]
            print(request.form["pswd"])
            pswd=request.form["pswd"]
            conn=sqlite3.connect("database1.db")
            print("database")
            cur=conn.cursor()
            print("cursor")
            cur.execute("SELECT * FROM login WHERE email=?;",(str(email),))
            print("fetch")
            result=cur.fetchone()
            if result:
                print("already")
                flash("user already exist,please login",'danger')
                return redirect('/')
            else:
                print("insert")
                cur.execute("INSERT INTO  login(email,password)values(?,?)",(str(email),str(pswd)))
                conn.commit()
                cur.execute("SELECT * FROM login")
                print(cur.fetchall())
                flash("Registered successfully",'success')
                return render_template('login.html')
            
        except Exception as e:
            print(e)
            return "hello error1"

@app.route('/home', methods=['GET','POST'])
def home():
    if(request.method=='POST'):
        gre = request.form.get('gre')
        toefl = request.form.get('toefl')
        urank = request.form.get('urank')
        sop = request.form.get('sop')
        lor = request.form.get('lor')
        cgpa = request.form.get('cgpa')
        research = request.form.get('research')

        t = [[gre, toefl, urank, sop, lor, cgpa, research]]


    # NOTE: manually define and pass the array(s) of values to be scored in the next line
        payload_scoring = {"input_data": [
        {"fields": [['GRE Score', 'TOEFL Score', 'University Rating', 'SOP', 'LOR', 'CGPA', 'Research']],
        "values": t}]}

        response_scoring = requests.post(
        'https://us-south.ml.cloud.ibm.com/ml/v4/deployments/0df064d7-25a2-42ee-b233-e8d970f891ac/predictions?version=2022-11-19',
        json=payload_scoring,
        headers={'Authorization': 'Bearer ' + mltoken})
        print("Scoring response")
        pred = response_scoring.json()
        output = pred['predictions'][0]['values'][0][0]
        return render_template("result.html", y=float(output))
    return render_template('mainpage.html')


if __name__ == "__main__":
    os.environ.setdefault('FLASK_ENV', 'development')
    app.run(debug=False)

