from email.errors import CloseBoundaryNotFoundDefect
from logging import exception
from flask import Flask, render_template, request, send_from_directory, jsonify
#from flask_cors import CORS #For Testing
import pymysql
import os
import json
import boto3
from config import *

app = Flask(__name__)
#CORS(app) #For Testing

bucket = custombucket
region = customregion


def create_connection():
    return pymysql.connect(
        host=customhost,
        db=customdb,
        user=customuser,
        password=custompass,
        port=3306
    )

def parse_employee(proc):
    parsed = []
    for item in proc:
        parsed.append({
            'emp_id':item[0],
            'first_name':item[1],
            'last_name':item[2],
            'pri_skill':item[3],
            'location':item[4]
        })
    return json.dumps(parsed)

def parse_attendance(proc):
    parsed = []
    for item in proc:
        parsed.append({
            'emp_id':item[0],
            'first_name':item[1],
            'last_name':item[2],
            'attend':item[3],
        })
    return json.dumps(parsed, default=str)


output = {}
table = 'employee'
# @app.route("/", defaults={"path": ""})
# @app.route("/<path:path>")
# def home(path):
#     return send_from_directory('static/public','index.html')
@app.route('/')
def base():
	return send_from_directory('static/public','index.html')

@app.route('/about')
def about():
	return send_from_directory('static/public','index.html')

@app.route('/manageEmp')
def manageemp():
	return send_from_directory('static/public','index.html')

@app.route('/empAttendance')
def attendance():
	return send_from_directory('static/public','index.html')

@app.route('/manageEmp/edit')
def editemp():
	return send_from_directory('static/public','index.html')
	
@app.route('/<path:path>')
def home(path):
    return send_from_directory('static/public',path)

# @app.route("/addemp", methods=['POST'])
# def AddEmp():
#     emp_id = request.form['emp_id']
#     first_name = request.form['first_name']
#     last_name = request.form['last_name']
#     pri_skill = request.form['pri_skill']
#     location = request.form['location']
#     emp_image_file = request.files['emp_image_file']

#     insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
#     connection = create_connection()
#     cursor = connection.cursor()

#     if emp_image_file.filename == "":
#         return "Please select a file"

#     try:

#         cursor.execute(insert_sql, (emp_id, first_name, last_name, pri_skill, location))
#         connection.commit()
#         emp_name = "" + first_name + " " + last_name
#         # Uplaod image file in S3 #
#         emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
#         s3 = boto3.resource('s3')

#         try:
#             print("Data inserted in MySQL RDS... uploading image to S3...")
#             s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
#             bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
#             s3_location = (bucket_location['LocationConstraint'])

#             if s3_location is None:
#                 s3_location = ''
#             else:
#                 s3_location = '-' + s3_location

#             object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
#                 s3_location,
#                 custombucket,
#                 emp_image_file_name_in_s3)

#         except Exception as e:
#             return str(e)

#     finally:
#         cursor.close()

#     print("all modification done...")
#     return render_template('AddEmpOutput.html', name=emp_name)

@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    emp_image_file = request.files['emp_image_file']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    connection = create_connection()
    cursor = connection.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (emp_id, first_name, last_name, pri_skill, location))
        connection.commit()
        emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            print(emp_image_file_name_in_s3)
            print(custombucket)
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            print(custombucket)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])
            print(s3_location)
            
            

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

            print(object_url)

        except Exception as e:
            print(e)
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('AddEmpOutput.html', name=emp_name)

@app.route("/readEmp",methods=['GET'])
def reademp():
    connection = create_connection()
    try:
        cursor = connection.cursor()
        query = 'SELECT emp_id,first_name, last_name, pri_skill, location FROM employee'
        cursor.execute(query)
        result = cursor.fetchall()
        print(parse_employee(result))
        return parse_employee(result),200
    except Exception as e:
        print(e)
    finally:
        connection.close()
    return "Error"

@app.route("/readEmpAttd",methods=['GET'])
def readempattd():
    att_date = request.args.get('date')
    print("arg " + att_date)
    connection = create_connection()
    try:
        cursor = connection.cursor()
        #query = "SELECT e.emp_id,first_name,last_name,date FROM employee e, attendance a WHERE date = DATE_FORMAT('{0}','%Y-%m-%d') AND e.emp_id = a.emp_id".format(att_date)
        query = "select employee.emp_id, employee.first_name, employee.last_name, attendance.attend from employee, attendance where employee.emp_id = attendance.emp_id AND attendance.att_date = DATE_FORMAT('{0}','%Y-%m-%d') union select employee.emp_id, employee.first_name, employee.last_name, null from employee where not exists(SELECT * from attendance where attendance.emp_id = employee.emp_id AND attendance.att_date = DATE_FORMAT('{0}','%Y-%m-%d')) order by emp_id".format(att_date)
        cursor.execute(query)
        result = cursor.fetchall()
        print(parse_attendance(result))
        return parse_attendance(result),200
    except Exception as e:
        print(e)
    finally:
        connection.close()
    return "Error"


@app.route("/delEmp")
def delemp():
    emp_id = request.args.get('emp_id')
    connection = create_connection()
    try:
        cursor = connection.cursor()
        sql = "DELETE FROM employee WHERE emp_id='{0}'".format(emp_id)
        cursor.execute(sql)
        return "Success",200
    except Exception as e:
        print(e)
    finally:
        connection.commit()
        connection.close()
    return "Error",400

@app.route("/addAttd")
def addattd():
    emp_id = request.args.get('emp_id')
    pass_date = request.args.get('date')
    attend = request.args.get('attend')
    connection = create_connection()
    try:
        cursor = connection.cursor()
        sql = "insert into attendance values ('{0}', DATE_FORMAT('{1}','%Y-%m-%d'), '{2}')".format(emp_id,pass_date,attend)
        cursor.execute(sql)
        return "Success",200
    except Exception as e:
        print(e)
    finally:
        connection.commit()
        connection.close()
    return "Error",400
    
@app.route("/delAttd")
def delattd():
    emp_id = request.args.get('emp_id')
    pass_date = request.args.get('date')
    connection = create_connection()
    try:
        cursor = connection.cursor()
        sql = "delete from attendance where emp_id = '{0}' AND att_date = DATE_FORMAT('{1}','%Y-%m-%d');".format(emp_id,pass_date)
        cursor.execute(sql)
        return "Success",200
    except Exception as e:
        print(e)
    finally:
        connection.commit()
        connection.close()
    return "Error",400
        
        


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5500, use_reloader=False)
