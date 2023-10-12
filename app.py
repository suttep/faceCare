from functools import wraps
from datetime import datetime, timedelta
from flask_session import Session
from flask import Flask, jsonify, redirect, render_template, request, session, make_response
from werkzeug.security import check_password_hash, generate_password_hash
import calendar
import sqlite3

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

con = sqlite3.connect('skincare.db', check_same_thread=False)

app.config["SESSION_TYPE"] = "filesystem"  # or other session types
app.config["SESSION_PERMANENT"] = False  # Optional, adjust as needed
app.config["SESSION_COOKIE_NAME"] = "skincareSession"

Session(app)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

cur = con.cursor()
@app.route("/", methods=["GET"])
def index():
    if session.get("user_id") is None:
        return render_template("index.html")
    else :
        getThisDay = datetime.strftime(datetime.now(), '%Y-%m-%d')
        earlierDate = datetime.today() - timedelta(days=7)

        cursorRoutine = con.execute("SELECT DISTINCT skinCycle, skincareLabel FROM skincareRoutine WHERE user_id = ?", (session["user_id"],))
        getRoutine  = cursorRoutine.fetchall()
        skincycleLabel = []
        for x in getRoutine:
            skincycleLabel.append(x[1])

        cursorUser = con.execute("SELECT * FROM skincareLog WHERE user_id = ?", (session["user_id"],))
        getUser  = cursorUser.fetchall()
        skincareStart = datetime.strptime(getUser[0][2], '%Y-%m-%d')

        if skincareStart >= earlierDate:
            userDay = earlierDate - skincareStart
        else:
            userDay = skincareStart - earlierDate

        userDay = userDay.days
        dayLog = userDay % 4
        count = 0
        cursorLogged = con.execute("SELECT routineDate FROM routineLog WHERE user_id = ?", (session["user_id"],))
        getLogged = cursorLogged.fetchall()
        earlierDays = []
        for index in range(14):
            dayNum = userDay + index
            today = 0
            logged = 0
            getDate = earlierDate + timedelta(index)
            dateForLog = datetime.strftime(getDate, '%Y-%m-%d')
            if dateForLog == getThisDay:
                today = 1
            for arr in getLogged:
                if dateForLog == arr[0]:
                    logged = 1

            routines = (dayLog + count) % 4
            if len(skincycleLabel) == 0:
                if routines == 3 :
                    routine = "Skin Barrier"
                elif routines == 2:
                    routine = "Skin Barrier"
                elif routines == 1:
                    routine = "Serums"
                else:
                    routine = "Exfoliation"
            else:
                if routines == 3:
                    routine = skincycleLabel[3]
                elif routines == 2:
                    routine = skincycleLabel[2]
                elif routines == 1:
                    routine = skincycleLabel[1]
                else:
                    routine = skincycleLabel[0]
            row = {"date": (earlierDate + timedelta(index)).strftime("%A, %d %B %Y"), "logged": logged, "routine":routine, "today":today, "number": dayNum}
            count += 1
            earlierDays.append(row)

        cursorUsername = con.execute("SELECT name FROM users WHERE user_id = ?", (session["user_id"],))
        getUsername = cursorUsername.fetchall()
        username = getUsername[0][0]

        if getUser[0][1] == 0:
            streak = "first"
        else:
            if getUser[0][1] == 1:
                streak = "first"
            else:
                streak = getUser[0][1]
        
        cursorLogger = con.execute("SELECT * FROM routineLog WHERE user_id = ? AND routineDate = ?", (session["user_id"], getThisDay))
        getLogger = cursorLogger.fetchall()
        if len(getLogger) == 1:
            logger = 1
        else:
            logger = 0
        return render_template("index-logged.html", username=username, streak=streak, logger=logger, earlierDays=earlierDays)

@app.route("/logout", methods=["GET"])
@login_required
def logout():
    session.clear()
    return redirect("/login")

@app.route("/register", methods=["GET"])
def register():
    return render_template("register.html")

@app.route("/generate", methods=["GET"])
def generateSkincare():
    return render_template("generateSkincare.html")

@app.route("/skincycle", methods=["GET"])
@login_required
def skincycle():
    cursorSkincycle = con.execute("SELECT * FROM skincareRoutine WHERE user_id = ?", (session["user_id"],))
    getSkincycle = cursorSkincycle.fetchall()
    skincycleLength = [0, 0, 0, 0, 0, 0, 0, 0]
    routineName = []
    mday1 = []
    nday1 = []
    mday2 = []
    nday2 = []
    mday3 = []
    nday3 = []
    mday4 = []
    nday4 = []
    for x in getSkincycle:
        if x[1] == 1 and x[2] == 1 and skincycleLength[0] == 0:
            skincycleLength[0] += 1
            mday1.append(x[5])
            routineName.append(x[4])
        elif x[1] == 1 and x[2] == 1:
            mday1.append(x[5])
            skincycleLength[0] += 1
        elif x[1] == 1 and x[2] == 2:
            nday1.append(x[5])
            skincycleLength[1] += 1
        elif x[1] == 2 and x[2] == 1 and skincycleLength[2] == 0:
            skincycleLength[2] += 1
            mday2.append(x[5])
            routineName.append(x[4])
        elif x[1] == 2 and x[2] == 1:
            mday2.append(x[5])
            skincycleLength[2] += 1
        elif x[1] == 2 and x[2] == 2:
            nday2.append(x[5])
            skincycleLength[3] += 1
        elif x[1] == 3 and x[2] == 1 and skincycleLength[4] == 0:
            skincycleLength[4] += 1
            mday3.append(x[5])
            routineName.append(x[4])
        elif x[1] == 3 and x[2] == 1:
            mday3.append(x[5])
            skincycleLength[4] += 1
        elif x[1] == 3 and x[2] == 2:
            nday3.append(x[5])
            skincycleLength[5] += 1
        elif x[1] == 4 and x[2] == 1 and skincycleLength[6] == 0:
            skincycleLength[6] += 1
            mday4.append(x[5])
            routineName.append(x[4])
        elif x[1] == 4 and x[2] == 1:
            mday4.append(x[5])
            skincycleLength[6] += 1
        elif x[1] == 4 and x[2] == 2:
            nday4.append(x[5])
            skincycleLength[7] += 1

    # if len(getSkincycle) == 0:
    cursorUser = con.execute("SELECT * FROM faceCondition WHERE user_id = ?", (session["user_id"],))
    getUser = cursorUser.fetchall()
    if len(getSkincycle) != 0:
        return render_template("skincycleEdit.html", user=getUser[0], routineName=routineName, skincycleLength=skincycleLength, mday1=mday1, nday1=nday1, mday2=mday2, nday2=nday2, mday3=mday3, nday3=nday3, mday4=mday4, nday4=nday4)
    else:
        return render_template("skincycle.html", user=getUser[0])
    # else:
        #should return edit skincycle
        # return

@app.post("/edit-skincycle")
def editSkincycle():
    mday1 = request.form.getlist('mday1')
    nday1 = request.form.getlist('nday1')
    mday2 = request.form.getlist('mday2')
    nday2 = request.form.getlist('nday2')
    mday3 = request.form.getlist('mday3')
    nday3 = request.form.getlist('nday3')
    mday4 = request.form.getlist('mday4')
    nday4 = request.form.getlist('nday4')

    getLabel1 = request.form.getlist("label1")
    label1 = getLabel1[0]
    getLabel2 = request.form.getlist("label2")
    label2 = getLabel2[0]
    getLabel3 = request.form.getlist("label3")
    label3 = getLabel3[0]
    getLabel4 = request.form.getlist("label4")
    label4 = getLabel4[0]

    i = 0
    con.execute("DELETE FROM skincareRoutine WHERE user_id = ?", (session["user_id"],))
    for name in mday1:
        con.execute("INSERT INTO skincareRoutine (user_id, skinCycle, skincareTime, skincarePosition, skincareLabel, skincareName) VALUES (?, ?, ?, ?, ?, ?)", (session["user_id"], 1, 1, i, label1, name))
        i += 1
    i = 0
    for name in nday1:
        con.execute("INSERT INTO skincareRoutine (user_id, skinCycle, skincareTime, skincarePosition, skincareLabel, skincareName) VALUES (?, ?, ?, ?, ?, ?)", (session["user_id"], 1, 2, i, label1, name))
        i += 1
    i = 0
    for name in mday2:
        con.execute("INSERT INTO skincareRoutine (user_id, skinCycle, skincareTime, skincarePosition, skincareLabel, skincareName) VALUES (?, ?, ?, ?, ?, ?)", (session["user_id"], 2, 1, i, label2, name))
        i += 1
    i = 0
    for name in nday2:
        con.execute("INSERT INTO skincareRoutine (user_id, skinCycle, skincareTime, skincarePosition, skincareLabel, skincareName) VALUES (?, ?, ?, ?, ?, ?)", (session["user_id"], 2, 2, i, label2, name))
        i += 1
    i = 0
    for name in mday3:
        con.execute("INSERT INTO skincareRoutine (user_id, skinCycle, skincareTime, skincarePosition, skincareLabel, skincareName) VALUES (?, ?, ?, ?, ?, ?)", (session["user_id"], 3, 1, i, label3, name))
        i += 1
    i = 0
    for name in nday3:
        con.execute("INSERT INTO skincareRoutine (user_id, skinCycle, skincareTime, skincarePosition, skincareLabel, skincareName) VALUES (?, ?, ?, ?, ?, ?)", (session["user_id"], 3, 2, i, label3, name))
        i += 1
    i = 0
    for name in mday4:
        con.execute("INSERT INTO skincareRoutine (user_id, skinCycle, skincareTime, skincarePosition, skincareLabel, skincareName) VALUES (?, ?, ?, ?, ?, ?)", (session["user_id"], 4, 1, i, label4, name))
        i += 1
    i = 0
    for name in nday4:
        con.execute("INSERT INTO skincareRoutine (user_id, skinCycle, skincareTime, skincarePosition, skincareLabel, skincareName) VALUES (?, ?, ?, ?, ?, ?)", (session["user_id"], 4, 2, i, label4, name))
        i += 1
    i = 0
    con.commit()
    return make_response(jsonify({"status": "success", "desc": "Skincycle updated.", "status-code": 200}))

@app.post("/input-skincycle")
def inputSkincycle():
    mday1 = request.form.getlist('mday1')
    nday1 = request.form.getlist('nday1')
    mday2 = request.form.getlist('mday2')
    nday2 = request.form.getlist('nday2')
    mday3 = request.form.getlist('mday3')
    nday3 = request.form.getlist('nday3')
    mday4 = request.form.getlist('mday4')
    nday4 = request.form.getlist('nday4')

    getLabel1 = request.form.getlist("label1")
    label1 = getLabel1[0]
    getLabel2 = request.form.getlist("label2")
    label2 = getLabel2[0]
    getLabel3 = request.form.getlist("label3")
    label3 = getLabel3[0]
    getLabel4 = request.form.getlist("label4")
    label4 = getLabel4[0]

    i = 0
    for name in mday1:
        con.execute("INSERT INTO skincareRoutine (user_id, skinCycle, skincareTime, skincarePosition, skincareLabel, skincareName) VALUES (?, ?, ?, ?, ?, ?)", (session["user_id"], 1, 1, i, label1, name))
        i += 1
    i = 0
    for name in nday1:
        con.execute("INSERT INTO skincareRoutine (user_id, skinCycle, skincareTime, skincarePosition, skincareLabel, skincareName) VALUES (?, ?, ?, ?, ?, ?)", (session["user_id"], 1, 2, i, label1, name))
        i += 1
    i = 0
    for name in mday2:
        con.execute("INSERT INTO skincareRoutine (user_id, skinCycle, skincareTime, skincarePosition, skincareLabel, skincareName) VALUES (?, ?, ?, ?, ?, ?)", (session["user_id"], 2, 1, i, label2, name))
        i += 1
    i = 0
    for name in nday2:
        con.execute("INSERT INTO skincareRoutine (user_id, skinCycle, skincareTime, skincarePosition, skincareLabel, skincareName) VALUES (?, ?, ?, ?, ?, ?)", (session["user_id"], 2, 2, i, label2, name))
        i += 1
    i = 0
    for name in mday3:
        con.execute("INSERT INTO skincareRoutine (user_id, skinCycle, skincareTime, skincarePosition, skincareLabel, skincareName) VALUES (?, ?, ?, ?, ?, ?)", (session["user_id"], 3, 1, i, label3, name))
        i += 1
    i = 0
    for name in nday3:
        con.execute("INSERT INTO skincareRoutine (user_id, skinCycle, skincareTime, skincarePosition, skincareLabel, skincareName) VALUES (?, ?, ?, ?, ?, ?)", (session["user_id"], 3, 2, i, label3, name))
        i += 1
    i = 0
    for name in mday4:
        con.execute("INSERT INTO skincareRoutine (user_id, skinCycle, skincareTime, skincarePosition, skincareLabel, skincareName) VALUES (?, ?, ?, ?, ?, ?)", (session["user_id"], 4, 1, i, label4, name))
        i += 1
    i = 0
    for name in nday4:
        con.execute("INSERT INTO skincareRoutine (user_id, skinCycle, skincareTime, skincarePosition, skincareLabel, skincareName) VALUES (?, ?, ?, ?, ?, ?)", (session["user_id"], 4, 2, i, label4, name))
        i += 1
    i = 0
    con.commit()
    return make_response(jsonify({"status": "success", "desc": "success", "status-code": 200}))

@app.route("/login", methods=["GET"])
def login():
    # if user not logged in
    if session.get("user_id") is None:
        return render_template("login.html")

    # if user is logged in
    else:
        session.clear()
        return render_template("login.html")

def getTime():
    now = datetime.now()
    return now.strftime("%Y-%m-%d")

@app.post("/input-login")
def inputLogin():
    if not request.form.get("email"):
        return make_response(jsonify({"status": "error", "desc": "Please insert correct email", "status-code": 403}))
    if not request.form.get("password"):
        return make_response(jsonify({"status": "error", "desc": "Please insert correct password", "status-code": 403}))

    email = request.form.get("email").lower()
    cursorRows = cur.execute("SELECT * FROM users WHERE email = ?", (email,))
    rows = cursorRows.fetchall()
    
    if len(rows) != 1:
        return make_response(jsonify({"status": "error", "desc": "Email doesn't exist", "status-code": 403}))

    if not check_password_hash(rows[0][3], request.form.get("password")):
        return make_response(jsonify({"status": "error", "desc": "Wrong password", "status-code": 403}))

    session["user_id"] = rows[0][0]

    return make_response(jsonify({"status": "success", "desc": "success", "status-code": 200}))

@app.post("/input-register")
def inputRegister():
    if not request.form.get("email"):
        return make_response(jsonify({"status": "error", "desc": "Please insert correct email", "status-code": 403}))
    if not request.form.get("name"):
        return make_response(jsonify({"status": "error", "desc": "Please insert correct name", "status-code": 403}))
    if not request.form.get("password"):
        return make_response(jsonify({"status": "error", "desc": "Please insert correct password", "status-code": 403}))
    if not request.form.get("skinType"):
        return make_response(jsonify({"status": "error", "desc": "Please choose correct skin type.", "status-code": 403}))

    time = getTime()
    email = request.form.get("email").lower()
    name = request.form.get("name")
    password = str(request.form.get("password"))
    passHash = generate_password_hash(password)
    skinType = request.form.get("skinType")


    # Query database for email
    cursorRows = con.execute("SELECT * FROM users WHERE email = ?", (request.form.get("email"),))
    rows = cursorRows.fetchall()
    # Ensure email not exists yet and password is correct
    if len(rows) == 1:
        return make_response(jsonify({"status": "error", "desc": "Email already exist", "status-code": 403}))

    con.execute("INSERT INTO users (email, name, password, registrationDate) VALUES(?, ?, ?, ?)", (email, name, passHash, time))
    con.commit()
    
    cursorRows = con.execute("SELECT * FROM users WHERE email = ?", (email,))
    rows = cursorRows.fetchall()
    
    acne = request.form.get("acne")
    if acne == "2":
        acneType = 0
    else:
        acneType = request.form.get("acneType")
    con.execute("INSERT INTO faceCondition (user_id, skinType, acneCondition, acneType, skincareDate) VALUES(?, ?, ?, ?, ?)", (rows[0][0], skinType, acne, acneType, time))
    con.commit()
    
    con.execute("INSERT INTO skincareLog (user_id, dayLog, skincareDateStart) VALUES(?, 0, ?)", (rows[0][0], time))
    con.commit()
    
    session["user_id"] = rows[0][0]

    return make_response(jsonify({"status": "success", "desc": acne, "status-code": 200}))

@app.route("/skincareGuide", methods=["GET"])
@login_required
def skincareGuide():
    cursorRows = con.execute("SELECT * FROM faceCondition WHERE user_id = ?", (session["user_id"],))
    rows = cursorRows.fetchall()
    return render_template("skincareGuide.html", skinType=rows[0][1], acneType=rows[0][3])

@app.post("/log_today")
@login_required
def logToday():
    time = getTime()
    cursorToday = con.execute("SELECT * FROM routineLog WHERE user_id = ? AND routineDate = ?", (session["user_id"], time))
    getToday = cursorToday.fetchall()
    if len(getToday) == 1:
        return make_response(jsonify({"status": "error", "desc": "You already log routine today.", "status-code": 403}))
    else:
        con.execute("INSERT INTO routineLog (user_id, routineDate) VALUES(?, ?)", (session["user_id"], time))
        con.commit()
        
        con.execute("UPDATE skincareLog SET dayLog = dayLog + 1  WHERE user_id = ?", (session["user_id"],))
        con.commit()
        return make_response(jsonify({"status": "success", "desc": "Success log routine for today.", "status-code": 200}))

@app.route("/history", methods=["GET"])
@login_required
def history():
    getThisDay = datetime.now().strftime("%d")
    getThisMonth = datetime.now().strftime("%m")
    getThisMonthName = datetime.now().strftime("%B")
    getThisYear = datetime.now().strftime("%Y")
    thisCalender = calendar.monthcalendar(int(getThisYear), int(getThisMonth))
    cursorLogged = con.execute("SELECT substr(routineDate,9,10) FROM routineLog WHERE user_id = ? AND routineDate LIKE ?", (session["user_id"], "%-"+getThisMonth+"-%"))
    getLogged = cursorLogged.fetchall()
    if len(getLogged) == None:
        getLogged = 0
    monthList = []


    cursorRoutine = con.execute("SELECT DISTINCT skinCycle, skincareLabel FROM skincareRoutine WHERE user_id = ?", (session["user_id"],))
    getRoutine = cursorRoutine.fetchall()
    skincycleLabel = []
    for x in getRoutine:
        skincycleLabel.append(x[1])

    cursorUser = con.execute("SELECT * FROM skincareLog WHERE user_id = ?", (session["user_id"],))
    getUser = cursorUser.fetchall()
    firstDay = datetime.strptime(getTime(), '%Y-%m-%d').replace(day=1)
    skincareStart = datetime.strptime(getUser[0][2], '%Y-%m-%d')
    #skincareStart erlier than firstDay of the month
    if skincareStart <= firstDay:
        userDay = firstDay - skincareStart
    else:
        userDay = skincareStart - firstDay

    userDay = userDay.days

    dayLog = userDay % 4
    count = 0
    for weeks in thisCalender:
        weekRow = []
        for days in weeks:
            logged = 0
            today = 0
            if int(days) == int(getThisDay):
                today = 1
            if len(getLogged) != 0:
                for logDay in getLogged:
                    if int(days) == int(logDay[0]):
                        logged = 1
            routines = (dayLog + count) % 4
            if len(skincycleLabel) == 0:
                if routines == 3 :
                    routine = "Skin Barrier"
                elif routines == 2:
                    routine = "Skin Barrier"
                elif routines == 1:
                    routine = "Serums"
                else:
                    routine = "Exfoliation"
            else:
                if routines == 3:
                    routine = skincycleLabel[3]
                elif routines == 2:
                    routine = skincycleLabel[2]
                elif routines == 1:
                    routine = skincycleLabel[1]
                else:
                    routine = skincycleLabel[0]
            row = {"date": days, "logged": logged, "routine":routine, "today":today}
            weekRow.append(row)
            count += 1
        monthList.append(weekRow)

    return render_template("history.html", monthList=monthList, getLogged=getLogged, monthName=getThisMonthName)

@app.route("/account", methods=["GET"])
@login_required
def account():
    cursorUser = con.execute("SELECT * FROM users WHERE user_id = ?", (session["user_id"],))
    getUser = cursorUser.fetchall()
    cursorFacecondition = con.execute("SELECT * FROM faceCondition WHERE user_id = ?", (session["user_id"],))
    getFacecondition = cursorFacecondition.fetchall()
    return render_template("account.html", user=getUser[0], facecondition=getFacecondition[0])

@app.post("/input-account")
def inputAccount():
    if not request.form.get("email"):
        return make_response(jsonify({"status": "error", "desc": "Please insert correct email", "status-code": 403}))
    if not request.form.get("name"):
        return make_response(jsonify({"status": "error", "desc": "Please insert correct name", "status-code": 403}))
    if not request.form.get("skinType"):
        return make_response(jsonify({"status": "error", "desc": "Please choose correct skin type.", "status-code": 403}))

    email = request.form.get("email").lower()
    name = request.form.get("name")
    skinType = request.form.get("skinType")
    acne = request.form.get("acne")


    # Query database for email
    cursorUserCurrentEmail = con.execute("SELECT * FROM users WHERE user_id = ? AND email = ?", (session["user_id"], request.form.get("email")))
    userCurrentEmail = cursorUserCurrentEmail.fetchall()
    if len(userCurrentEmail) != 1:
        cursorEmailCheck = con.execute("SELECT * FROM users WHERE email = ?", (request.form.get("email"),))
        emailCheck = cursorEmailCheck.fetchall()
        # Ensure email not exists yet and password is correct
        if len(emailCheck) == 1:
            return make_response(jsonify({"status": "error", "desc": "Email already exist", "status-code": 403}))

    con.execute("UPDATE users SET email = ?, name = ? WHERE user_id = ?", (email, name, session["user_id"]))
    con.commit()
    
    if acne == "2":
        acneType = 0
    else:
        acneType = request.form.get("acneType")
    con.execute("UPDATE faceCondition SET skinType = ?, acneCondition = ?, acneType = ? WHERE user_id = ?", (skinType, acne, acneType, session["user_id"]))
    con.commit()
    return make_response(jsonify({"status": "success", "desc": "Saved new account configuration.", "status-code": 200}))

if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0")