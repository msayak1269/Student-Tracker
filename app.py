from flask import (
    Flask, render_template, redirect, request, url_for, flash, make_response, jsonify
)
from auth import auth
import os
import json
import uuid

app = Flask(__name__, static_url_path="")
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
app.secret_key = "thisisasecretkey"

APP_ROOT = os.path.dirname(os.path.abspath(__file__))


@app.route("/SignUp")
def SignUp():
    return render_template("signup.html")


@app.route("/SigningUp", methods=["POST"])
def SigningUp():
    name = request.form.get("name")
    email = request.form.get("email")
    pin1 = request.form.get("pin1")
    pin2 = request.form.get("pin2")
    subject = request.form.get("subject")

    if pin1 != pin2:
        flash("!!!Pin not matched,Try again!!!")
        return redirect(url_for("SignUp"))
    else:
        user_detail = {
            "id": str(uuid.uuid4()),
            "name": name,
            "email": email,
            "pin": pin1,
            "subject": subject,
            "flag": 0
        }

        json_file = open(f"{APP_ROOT}/db/user.json", "r")
        all_user = json.load(json_file)
        json_file.close()
        all_user.append(user_detail)
        json_file = open(f"{APP_ROOT}/db/user.json", "w")
        json_file.seek(0)
        json.dump(all_user, json_file, indent=2)
        json_file.close()

        json_file = open(f"{APP_ROOT}/db/student.json", "r")
        student = json.load(json_file)
        json_file.close()
        flash("!!! Sign Up Successfull !!!")
        return redirect(url_for("SignIn",color = "success"))


@app.route("/")
def SignIn():
    if request.cookies.get("abc"):
        return redirect(url_for("Home"))
    return render_template("login.html")


@app.route("/SigningIn", methods=["GET", "POST"])
def SigningIn():
    if request.method == "GET":
        return redirect(url_for("SignIn"))
    else:
        email = request.form.get("email")
        pin = request.form.get("pin")

        isSignedUp, user = auth.checkLogin(APP_ROOT, email, pin)
        if isSignedUp:
            resp = make_response(redirect(url_for("Home")))
            resp.set_cookie("abc", email, max_age=60*60*24*365*2)
            flash("!!! Log in Successfull !!!")
            return resp
        else:
            flash("!!! Invalid credentials !!!")
            return redirect(url_for("SignIn",color = "danger"))


@app.route("/Home")
def Home():
    if request.cookies.get("abc"):
        userEmail = request.cookies.get("abc")
        json_file = open(f"{APP_ROOT}/db/user.json", "r")
        all_user = json.load(json_file)
        json_file.close()
        user = {}
        for usr in all_user:
            if userEmail == usr["email"]:
                user = usr
                break
        json_file = open(f"{APP_ROOT}/db/student.json", "r")
        student = json.load(json_file)
        json_file.close()  
        count = 0
        # count = student[userEmail]["counter"]
        return render_template("home.html", userEmail=userEmail,user = user,count = count)
    else:
        return redirect(url_for("SignIn"))


@app.route("/add")
def addStudent():
    if request.cookies.get("abc"):
        return render_template("form.html")
    else:
        return redirect(url_for("SignIn"))    


@app.route("/submit", methods=["POST"])
def submit():
    stname = request.form.get("stname")
    grdname = request.form.get("grdname")
    schlname = request.form.get("schlname")
    cls = request.form.get("cls")
    doj = request.form.get("doj")
    stno = request.form.get("stno")
    grdno = request.form.get("grdno")
    whtsap = request.form.get("whtsap")
    email = request.form.get("email")

    imageName = "male.jpg"
    target = APP_ROOT+'/static/images'
    imageFile = request.files.get("image")
    if imageFile:
        imageName = imageFile.filename
        destination = "/".join([target, imageName])
        imageFile.save(destination)

    student_detail = {

        "id": str(uuid.uuid4()),
        "stname": stname,
        "image": imageName,
        "grdname": grdname,
        "schlname": schlname,
        "cls": cls,
        "doj": doj,
        "stno": stno,
        "grdno": grdno,
        "whtsap": whtsap,
        "email": email
    }
    FeeOfMonth = [0,0,0,0,0,0,0,0,0,0,0,0]

    joinDate = int(doj[-2]+doj[-1])
    joinMonth = (int(doj[-5]+doj[-4]))-1

    if joinDate > 15 and joinMonth != 11:
        FeeOfMonth[joinMonth]=1
    
    student_detail1 = {
        "id":str(student_detail["id"]),
        "stname": stname,
        "image": imageName,
        "grdname": grdname,
        "schlname": schlname,
        "cls": cls,
        "doj": doj,
        "stno": stno,
        "grdno": grdno,
        "whtsap": whtsap,
        "email": email,
        "fee":FeeOfMonth
    }

    
    json_file = open(f"{APP_ROOT}/db/data.json", "r")
    all_student = json.load(json_file)
    json_file.close()
    all_student.append(student_detail1)
    json_file = open(f"{APP_ROOT}/db/data.json", "w")
    json_file.seek(0)
    json.dump(all_student, json_file, indent=2)
    json_file.close()

    userEmail = request.cookies.get("abc")
    json_file = open(f"{APP_ROOT}/db/student.json", "r")
    student = json.load(json_file)
    json_file.close()

    if userEmail in student:
        students_of_user = student[userEmail]
        if cls in students_of_user:
            students = students_of_user[cls]
            students.append(student_detail)
        else:
            new_cls = {cls: []}
            students_of_user.update(new_cls)
            students = students_of_user[cls]
            students.append(student_detail)
        students_of_user["counter"] += 1
    else:
        new_user = {userEmail: {}}
        student.update(new_user)
        students_of_user = {"counter": 1, cls: []}
        students_of_user[cls].append(student_detail)
        student[userEmail].update(students_of_user)

        json_file = open(f"{APP_ROOT}/db/user.json", "r")
        all_user = json.load(json_file)
        json_file.close()

        for user in all_user:
            if user["email"] == userEmail:
                user["flag"] = 1

        json_file = open(f"{APP_ROOT}/db/user.json", "w")
        json_file.seek(0)
        json.dump(all_user, json_file, indent=2)
        json_file.close()

    json_file = open(f"{APP_ROOT}/db/student.json", "w")
    json_file.seek(0)
    json.dump(student, json_file, indent=2)

    return redirect(url_for("Home"))


@app.route("/view")
def viewDetails():
    if request.cookies.get("abc"):
        json_file = open(f"{APP_ROOT}/db/user.json", "r")
        all_user = json.load(json_file)
        json_file.close()

        userEmail = request.cookies.get("abc")

        for user in all_user:
            if user["email"] == userEmail and user["flag"] == 0:
                flash("No students yet!")
                return redirect(url_for("Home"))

        json_file = open(f"{APP_ROOT}/db/student.json", "r")
        student = json.load(json_file)
        json_file.close()

        students_of_user = student[userEmail]
        counts = {}
        for key, value in students_of_user.items():
            if key != "counter":
                counts.update({key: len(value)})
        total = students_of_user["counter"]
        return render_template("detail.html", counts=counts, total=total)
    else:
        return redirect(url_for("SignIn"))

@app.route("/view/class/<classId>")
def ClassDetails(classId):
    if request.cookies.get("abc"):
        userEmail = request.cookies.get("abc")
        json_file = open(f"{APP_ROOT}/db/student.json", "r")
        student = json.load(json_file)
        json_file.close()
        students_of_user = student[userEmail]
        studentList = []
        for key, value in students_of_user.items():
            if str(key) == str(classId):
                studentList = value
                classId = str(key)
                break
        return render_template("classdetail.html", studentList=studentList,classId = classId )
    else:
        return redirect(url_for("SignIn"))


@app.route("/view/class/<classId>/student/<studentId>")
def ViewStudentDetail(classId , studentId):
    if request.cookies.get("abc"):
        userEmail = request.cookies.get("abc")
        json_file = open(f"{APP_ROOT}/db/student.json", "r")
        student = json.load(json_file)
        json_file.close()
        students_of_user = student[userEmail]
        classList = students_of_user[classId]
        foundStudent = {}
        for student in classList:
            if str(student["id"]) == str(studentId):
                foundStudent = student
                break
        return render_template("card.html", student=foundStudent)
    else:
        return redirect(url_for("SignIn")) 







@app.route("/student/<studentId>/delete")
def delete(studentId):
    if request.cookies.get("abc"):
        new_details = []
        json_file = open(f"{APP_ROOT}/db/data.json", "r")
        datas = json.load(json_file)
        json_file.close()
        # imageToBeDeleted = ""
        for data  in datas:
            if data["id"]==studentId:
                student = data
        for data in datas:
            if data["id"]!=studentId:
                new_details.append(data)
        json_file = open(f"{APP_ROOT}/db/data.json", "w")
        json_file.seek(0)
        json.dump(new_details, json_file, indent=2)
        json_file.close()

        json_file = open(f"{APP_ROOT}/db/student.json", "r")
        all_student = json.load(json_file)
        json_file.close()

        userEmail = request.cookies.get("abc")

        studentClass = student["cls"]
        
        studentsOfaClass = all_student[userEmail][studentClass]

        studentsOfaClass1=[]

        for st in studentsOfaClass:
            if st["id"]!=str(studentId):
                studentsOfaClass1.append(st)
        
        all_student[userEmail][studentClass] = studentsOfaClass1

        if len(all_student[userEmail][studentClass])==0:
            del all_student[userEmail][studentClass]
        all_student[userEmail]["counter"]-=1    

        json_file = open(f"{APP_ROOT}/db/student.json", "w")
        json_file.seek(0)
        json.dump(all_student, json_file, indent=2)
        json_file.close()


        # if imageToBeDeleted=="male.jpg":
        #     pass
        # else:
        #     os.remove(f"{APP_ROOT}/static/images/{imageToBeDeleted}")
        if all_student[userEmail]["counter"]==0:
            json_file = open(f"{APP_ROOT}/db/user.json", "r")
            all_user = json.load(json_file)
            json_file.close()
            for user in all_user:
                if user["email"] == userEmail:
                    user["flag"]=0
                    break
            resp = make_response(redirect(url_for("Home")))
            flash("No Student!!!")
            return resp
        else:    
            return redirect("/view")
    else:
        return redirect(url_for("SignIn"))

@app.route("/student/updateform/<studentId>")
def UpdateForm(studentId):
    if request.cookies.get("abc"):
        userEmail = request.cookies.get("abc")
        json_file = open(f"{APP_ROOT}/db/data.json", "r")
        all_student = json.load(json_file)
        json_file.close()
        updtStudent = {}
        for st in all_student:
            if str(st["id"]) == str(studentId):
                updtStudent = st
                break
        return render_template("updateform.html",student = updtStudent)
    else:
        return redirect(url_for("SignIn"))


@app.route("/student/updateform/<studentId>/update", methods=["POST"])
def updateStudent(studentId):
    if request.cookies.get("abc"):
        userEmail = request.cookies.get("abc")
        json_file = open(f"{APP_ROOT}/db/data.json", "r")
        datas = json.load(json_file)
        json_file.close()

        stname = request.form.get("stname")
        grdname = request.form.get("grdname")
        schlname = request.form.get("schlname")
        #cls = request.form.get("cls")
        #doj = request.form.get("doj")
        stno = request.form.get("stno")
        grdno = request.form.get("grdno")
        whtsap = request.form.get("whtsap")
        email = request.form.get("email")
        cls = ""
        for data in datas:
            if data["id"]==studentId:
                data["stname"]=stname
                data["grdname"]=grdname
                data["schlname"]=schlname
                data["stno"]=stno
                data["grdno"]=grdno
                data["whtsap"]=whtsap
                data["email"]=email
                cls = data["cls"]
                break
        json_file = open(f"{APP_ROOT}/db/data.json","w")
        json_file.seek(0)
        json.dump(datas, json_file, indent=2)
        json_file.close()

        json_file = open(f"{APP_ROOT}/db/student.json", "r")
        datas = json.load(json_file)
        json_file.close()
        studentList = datas[userEmail][cls]
        for student in studentList:
            if student["id"]==studentId:
                student["stname"]=stname
                student["grdname"]=grdname
                student["schlname"]=schlname
                student["stno"]=stno
                student["grdno"]=grdno
                student["whtsap"]=whtsap
                student["email"]=email
        json_file = open(f"{APP_ROOT}/db/student.json","w")
        json_file.seek(0)
        json.dump(datas, json_file, indent=2)
        json_file.close()
        redirectUrl = f"/view/class/{cls}/student/{studentId}"
        return redirect(redirectUrl)
    else:
        return redirect(url_for("SignIn"))


@app.route("/fee/<studentId>")
def FeeStatus(studentId):
    if request.cookies.get("abc"):
        month = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]

        json_file = open(f"{APP_ROOT}/db/data.json", "r")
        all_student = json.load(json_file)
        json_file.close()
        student = {}
        studentFee = []
        for st in all_student:
            if st["id"] == str(studentId):
                student = st
                break
        
        studentFee = st["fee"]

        userEmail = request.cookies.get("abc")
        json_file = open(f"{APP_ROOT}/db/user.json", "r")
        users = json.load(json_file)
        json_file.close()
        user={}
        for usr in users:
            if str(usr["email"]) == str(userEmail):
                user = usr
                break
        return render_template("month.html",month=month,start = 1,end = 13,student = student,user = user, studentFee=studentFee)
    else:
        return redirect(url_for("SignIn")) 


@app.route("/fee/<studentId>/<month>/update", methods=["POST"])
def updateFee(studentId,month):
    if request.cookies.get("abc"):
        json_file = open(f"{APP_ROOT}/db/data.json", "r")
        all_student = json.load(json_file)
        json_file.close()
        student = {}
        for st in all_student:
            if st["id"] == str(studentId):
                student = st
                break
        student["fee"][int(month)]=1

        json_file = open(f"{APP_ROOT}/db/data.json", "w")
        json_file.seek(0)
        json.dump(all_student, json_file, indent=2)
        json_file.close()
        resp = {"message": "success"}
        return jsonify(resp)
    else:
        return redirect(url_for("SignIn"))


@app.route("/account")
def account():
    if request.cookies.get("abc"):
        userEmail = request.cookies.get("abc")
        json_file = open(f"{APP_ROOT}/db/user.json", "r")
        users = json.load(json_file)
        json_file.close()
        account = {}
        for user in users:
            if user["email"]==userEmail:
                account = user
                break
        json_file = open(f"{APP_ROOT}/db/student.json", "r")
        students = json.load(json_file)
        json_file.close()
        c = 0
        c = students[userEmail]["counter"]
        return render_template("account.html", account=account,counter = c)
    else:
        return redirect(url_for("SignIn"))


@app.route("/logout")
def logout():
    resp = make_response(redirect(url_for('SignIn')))
    resp.set_cookie('abc', expires=0)
    return resp    


if __name__=="__main__":
    app.run(port=5001, debug=True, host='0.0.0.0')
