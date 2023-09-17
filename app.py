import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from datetime import date, datetime

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/landing")
        return f(*args, **kwargs)

    return decorated_function

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///zen.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

##############
# BACKGROUND #
##############

@app.route("/background")
def background():
    return render_template("background.html")


#########
# ABOUT #
#########

@app.route("/about")
@login_required
def about():
    return render_template("about.html")

############
# ADD MEAL #
############

@app.route("/add-meal", methods=["GET", "POST"])
@login_required
def add_meal():
    if request.method == "POST":
        if request.form.get("meal_name"):
            meal_name = request.form.get("meal_name")
        else:
            meal_name = "Meal"

        if request.form.get("meal_date"):
            meal_date = request.form.get("meal_date")
        else:
            meal_date = str(date.today())

        food_id = request.form.get("food_id")
        amount = request.form.get("amount")
        db.execute("INSERT INTO user_meals (user_id, meal_date, meal_name, food_id, amount) VALUES (?, ?, ?, ?, ?)", session["user_id"], meal_date, meal_name, food_id, amount)
        return redirect("/diary")
    else:
        food_data = db.execute("SELECT * FROM food_data")# WHERE user_id = ?", session["user_id"])
        return render_template("add-meal.html", food_data=food_data)
    
############
# ADD FOOD #
############

@app.route("/add-food", methods=["GET", "POST"])
@login_required
def add_food():
    if request.method == "POST":
        food_name = request.form.get("food_name")

        print(request.form.get("food_uom"))

        if (request.form.get("food_uom") != "u") and (request.form.get("food_uom") != "ml") and (request.form.get("food_uom") != "g"):
            flash('Must provide a valid Unit of Measurement')
            return redirect("/add-food")
        
        food_uom = request.form.get("food_uom")
        food_calories = int(request.form.get("food_calories"))
        food_protein = float(request.form.get("food_protein"))
        food_carbs = float(request.form.get("food_carbs"))
        food_fats = float(request.form.get("food_fats"))

        db.execute(
            "INSERT INTO food_data (user_id, food_name, food_uom, food_calories, food_protein, food_carbs, food_fats) VALUES (?, ?, ?, ?, ?, ?, ?)",
            session["user_id"], food_name, food_uom, food_calories, food_protein, food_carbs, food_fats
        )
        return redirect("/add-meal")
    else:
        return render_template("add-food.html")

##########
# DELETE #
##########

@app.route("/delete", methods=["POST"])
def delete():

    meal_id = request.form.get("meal_id")
    if meal_id:
        db.execute("DELETE FROM user_meals WHERE user_id = ? AND meal_id = ?", session["user_id"], meal_id)
    return redirect("/diary")

#########
# DIARY #
#########

@app.route("/diary", methods=["GET", "POST"])
@login_required
def diary():
    if request.method == "POST":
        current_date = request.form.get("date")
        user_diary = db.execute(
            "SELECT * FROM user_meals JOIN food_data ON user_meals.food_id=food_data.food_id WHERE user_meals.meal_date = ? AND user_meals.user_id = ?",
            current_date, session["user_id"]
        )

        total_cal = 0
        total_protein = 0
        total_carbs = 0
        total_fats = 0
        for meal in user_diary:
            food_item = db.execute("SELECT * FROM food_data WHERE food_id = ?", meal["food_id"])
            food_amount = meal["amount"]
            food_calories = food_item[0]["food_calories"]
            food_protein = food_item[0]["food_protein"]
            food_carbs = food_item[0]["food_carbs"]
            food_fats = food_item[0]["food_fats"]

            if food_item[0]["food_uom"] == "u":
                total_cal += food_calories * food_amount
                total_protein += food_protein * food_amount
                total_carbs += food_carbs * food_amount
                total_fats += food_fats * food_amount
            else:
                total_cal += food_calories / 100 * food_amount
                total_protein += food_protein / 100 * food_amount
                total_carbs += food_carbs / 100 * food_amount
                total_fats += food_fats / 100 * food_amount

        return render_template("diary.html", user_diary=user_diary, current_date=current_date, total_cal=int(total_cal), total_protein=round(total_protein, 2),
            total_carbs=round(total_carbs, 2), total_fats=round(total_fats, 2))
    else:
        user = db.execute('SELECT * FROM personal_info WHERE id = ?', session["user_id"])
        try:
            user[0]["tdee"]
        except IndexError:
            flash('You must complete your profile setup before moving on')
            return redirect("/profile-setup")
        current_date = datetime.today().strftime('%Y-%m-%d')
        today = str(date.today())
        user_diary = db.execute(
            "SELECT * FROM user_meals JOIN food_data ON user_meals.food_id=food_data.food_id WHERE user_meals.meal_date = ? AND user_meals.user_id = ?", today, session["user_id"]
        )
        
        total_cal = 0
        total_protein = 0
        total_carbs = 0
        total_fats = 0
        for meal in user_diary:
            food_item = db.execute("SELECT * FROM food_data WHERE food_id = ?", meal["food_id"])
            food_amount = meal["amount"]
            food_calories = food_item[0]["food_calories"]
            food_protein = food_item[0]["food_protein"]
            food_carbs = food_item[0]["food_carbs"]
            food_fats = food_item[0]["food_fats"]

            if food_item[0]["food_uom"] == "u":
                total_cal += food_calories * food_amount
                total_protein += food_protein * food_amount
                total_carbs += food_carbs * food_amount
                total_fats += food_fats * food_amount
            else:
                total_cal += food_calories / 100 * food_amount
                total_protein += food_protein / 100 * food_amount
                total_carbs += food_carbs / 100 * food_amount
                total_fats += food_fats / 100 * food_amount

        return render_template("diary.html", user_diary=user_diary, current_date=current_date, total_cal=int(total_cal), total_protein=round(total_protein, 2),
            total_carbs=round(total_carbs, 2), total_fats=round(total_fats, 2))

########
# HOME #
########

@app.route("/")
@login_required
def index():
    today = str(date.today())
    current_calories = 0
    current_protein = 0
    current_carbs = 0
    current_fats = 0
    todays_meals = db.execute("SELECT * FROM user_meals WHERE meal_date = ? AND user_id = ?", today, session["user_id"])

    for meal in todays_meals:
        food_item = db.execute("SELECT * FROM food_data WHERE food_id = ?", meal["food_id"])
        food_amount = meal["amount"]
        food_calories = food_item[0]["food_calories"]
        food_protein = food_item[0]["food_protein"]
        food_carbs = food_item[0]["food_carbs"]
        food_fats = food_item[0]["food_fats"]

        if food_item[0]["food_uom"] == "u":
            current_calories += food_calories * food_amount
            current_protein += food_protein * food_amount
            current_carbs += food_carbs * food_amount
            current_fats += food_fats * food_amount
        else:
            current_calories += food_calories / 100 * food_amount
            current_protein += food_protein / 100 * food_amount
            current_carbs += food_carbs / 100 * food_amount
            current_fats += food_fats / 100 * food_amount

    user = db.execute("SELECT * FROM personal_info WHERE id = ?", session["user_id"])
    try:
        tdee = int(user[0]["tdee"])
    except IndexError:
        flash('You must complete your profile setup before moving on')
        return redirect("/profile-setup")
    
    objective = user[0]["objective"]

    if objective == 1:
        tdee -= 500
    elif objective == 3:
        tdee += 500

    protein_goal = int(((tdee / 100)* 30) / 4)
    carbs_goal = int(((tdee / 100)* 35) / 4)
    fats_goal = int(((tdee / 100)* 35) / 9)

    current_percentage = round((float(current_calories) / float(tdee)) * 100.00)

    return render_template("home.html", tdee=tdee, protein_goal=protein_goal, carbs_goal=carbs_goal, fats_goal=fats_goal, current_calories=round(current_calories),
        current_protein=round(current_protein, 2), current_carbs=round(current_carbs, 2), current_fats=round(current_fats, 2), current_percentage=current_percentage)

###########
# LANDING #
###########

@app.route("/landing")
def landing():
    return render_template("landing.html")

###############################
# LOG IN - LOG OUT - REGISTER #
###############################

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            flash('You must provide a username')
            return redirect("/login")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash('You must provide a password')
            return redirect("/login")

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            flash('Invalid username or password')
            return redirect("/login")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    """Register user"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        users = db.execute("SELECT * FROM users")

        # Ensure username was submitted
        if not request.form.get("username"):
            flash('You must provide a valid username')
            return redirect("/sign-up")

        validUser = True
        for user in users:
            if request.form.get("username") == user["username"]:
                validUser = False

        if not validUser:
            flash('That username is already taken')
            return redirect("/sign-up")

        # Ensure password was submitted
        if not request.form.get("password"):
            flash('You must provide a password')
            return redirect("/sign-up")

        # Ensure password and confirmation match
        if request.form.get("password") != request.form.get("confirmation"):
            flash('Password and confirmation must match')
            return redirect("/sign-up")

        # Save user's data into database
        username = request.form.get("username")
        hash = generate_password_hash(
            request.form.get("password"), method="pbkdf2:sha256", salt_length=8
        )
        db.execute(
            "INSERT INTO users (username, hash) VALUES (?, ?)", username, hash
        )

        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", username
        )
        
        session["user_id"] = rows[0]["id"]

        # Redirect user to step two
        return redirect("/profile-setup")
    else:
        return render_template("sign-up.html")
    
#################
# PROFILE SETUP #
#################
    
@app.route("/profile-setup", methods=["GET", "POST"])
@login_required
def profile_setup():
    if request.method == "POST":
        id = session["user_id"]
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        age = int(request.form.get("age"))
        sex = request.form.get("sex")
        height = int(request.form.get("height"))
        weight = int(request.form.get("weight"))
        activity = float(request.form.get("activity"))
        objective = int(request.form.get("objective"))
        try:
            bodyfat_percentage = int(request.form.get("bodyfat_percentage"))
        except ValueError:
            bodyfat_percentage = 0

        if bodyfat_percentage != 0:
            lbm = weight * (1 - (bodyfat_percentage * 0.01))

            bmr = 370 + (21.6 * lbm)
        elif sex == "m":
            bmr = (10 * float(weight)) + (6.25 * float(height)) - (5 * float(age)) + 5
        else:
            bmr = (10 * float(weight)) + (6.25 * float(height)) - (5 * float(age)) - 161

        tdee = bmr * activity
        
        db.execute(
            "INSERT INTO personal_info (firstname, lastname, age, sex, height, weight, activity, objective, bodyfat_percentage, bmr, tdee, id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            firstname, lastname, age, sex, height, weight, activity, objective, bodyfat_percentage, bmr, tdee, id
        )

        return redirect("/")
    else:
        return render_template("profile-setup.html")
    
############
# SETTINGS #
############

@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    if request.method == "POST":
        user = db.execute('SELECT * FROM personal_info WHERE id = ?', session["user_id"])
        weight = user[0]["weight"]
        height = user[0]["height"]
        sex = user[0]["sex"]
        age = user[0]["age"]
        activity = user[0]["activity"]
        bodyfat_percentage = user[0]["bodyfat_percentage"]

        if request.form.get("firstname"):
            db.execute(
                "UPDATE personal_info SET firstname = ? WHERE id = ?", request.form.get("firstname"), session["user_id"]
            )

        if request.form.get("lastname"):
            db.execute(
                "UPDATE personal_info SET lastname = ? WHERE id = ?", request.form.get("lastname"), session["user_id"]
            )

        if request.form.get("age"):
            age = int(request.form.get("age"))
            db.execute(
                "UPDATE personal_info SET age = ? WHERE id = ?", request.form.get("age"), session["user_id"]
            )

        if request.form.get("sex"):
            sex = request.form.get("sex")
            db.execute(
                "UPDATE personal_info SET sex = ? WHERE id = ?", request.form.get("sex"), session["user_id"]
            )

        if request.form.get("height"):
            height = int(request.form.get("height"))
            db.execute(
                "UPDATE personal_info SET height = ? WHERE id = ?", request.form.get("height"), session["user_id"]
            )

        if request.form.get("weight"):
            weight = int(request.form.get("weight"))
            db.execute(
                "UPDATE personal_info SET weight = ? WHERE id = ?", request.form.get("weight"), session["user_id"]
            )

        if request.form.get("activity"):
            activity = float(request.form.get("activity"))
            db.execute(
                "UPDATE personal_info SET activity = ? WHERE id = ?", request.form.get("activity"), session["user_id"]
            )
        
        if request.form.get("objective"):
            db.execute(
                "UPDATE personal_info SET objective = ? WHERE id = ?", request.form.get("objective"), session["user_id"]
            )

        if request.form.get("bodyfat_percentage"):
            bodyfat_percentage = int(request.form.get("bodyfat_percentage"))
            db.execute(
                "UPDATE personal_info SET bodyfat_percentage = ? WHERE id = ?", request.form.get("bodyfat_percentage"), session["user_id"]
            )

        

        if bodyfat_percentage != 0:
            lbm = weight * (1 - (bodyfat_percentage * 0.01))

            bmr = 370 + (21.6 * lbm)
            db.execute("UPDATE personal_info SET bmr = ? WHERE id = ?", bmr, session["user_id"])
        elif sex == "m":
            bmr = (10 * float(weight)) + (6.25 * float(height)) - (5 * float(age)) + 5
            db.execute("UPDATE personal_info SET bmr = ? WHERE id = ?", bmr, session["user_id"])
        else:
            bmr = (10 * float(weight)) + (6.25 * float(height)) - (5 * float(age)) - 161
            db.execute("UPDATE personal_info SET bmr = ? WHERE id = ?", bmr, session["user_id"])

        tdee = bmr * activity
        db.execute("UPDATE personal_info SET tdee = ? WHERE id = ?", tdee, session["user_id"])
        return redirect("/")
    else:
        user = db.execute('SELECT * FROM personal_info WHERE id = ?', session["user_id"])
        try:
            user[0]["tdee"]
        except IndexError:
            flash('You must complete your profile setup before moving on')
            return redirect("/profile-setup")
        
        return render_template("settings.html", user=user)