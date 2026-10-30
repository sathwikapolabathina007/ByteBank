from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime
from models import db
from models.user import User
from models.income import Income
from models.expense import Expense
from models.budget import Budget

app = Flask(__name__)

# Secret Key
app.config["SECRET_KEY"] = "bytebank_secret_key"

# SQLite Database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bytebank.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize Database
db.init_app(app)
# Flask Login
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create Database
with app.app_context():
    db.create_all()

# ---------------- Routes ---------------- #

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/features")
def features():
    return render_template("features.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("An account with this email already exists.", "danger")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)

        new_user = User(
            username=username,
            email=email,
            password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("dashboard"))

        flash("Invalid email or password.", "danger")

    return render_template("login.html")


@app.route("/dashboard")
@login_required
def dashboard():

    # Get selected month from URL
    selected_month = request.args.get("month")

    if selected_month:
        try:
            selected_year, selected_month_number = map(
                int,
                selected_month.split("-")
            )
        except (ValueError, TypeError):
            selected_year = datetime.now().year
            selected_month_number = datetime.now().month
    else:
        selected_year = datetime.now().year
        selected_month_number = datetime.now().month

    incomes = Income.query.filter_by(
        user_id=current_user.id
    ).all()

    expenses = Expense.query.filter_by(
        user_id=current_user.id
    ).all()

    # Calculate totals
    total_income = sum(i.amount for i in incomes)
    total_expense = sum(e.amount for e in expenses)
    total_balance = total_income - total_expense

    # Get current month and year
        # Get budget for the selected month
    current_budget = Budget.query.filter_by(
        user_id=current_user.id,
        month=selected_month_number,
        year=selected_year
    ).first()

    # Calculate expenses only for the current month
    monthly_budget_expenses = []

    for expense in expenses:

        try:

            expense_date = str(expense.date)

            expense_year = int(expense_date[:4])
            expense_month = int(expense_date[5:7])

            if (
            expense_year == selected_year
            and expense_month == selected_month_number
            ):
                monthly_budget_expenses.append(expense.amount)

        except (ValueError, TypeError, IndexError):
            pass

    # Calculate total spent for the current month
    budget_spent = sum(monthly_budget_expenses)

    # Calculate budget details
    if current_budget:

        budget_amount = current_budget.amount

        budget_remaining = (
            budget_amount - budget_spent
        )

        if budget_amount > 0:

            budget_percentage = (
                budget_spent / budget_amount
            ) * 100

        else:

            budget_percentage = 0

    else:

        budget_amount = 0
        budget_remaining = 0
        budget_percentage = 0

    # Prepare monthly data for analytics
    monthly_income = {
        "Jan": 0,
        "Feb": 0,
        "Mar": 0,
        "Apr": 0,
        "May": 0,
        "Jun": 0,
        "Jul": 0,
        "Aug": 0,
        "Sep": 0,
        "Oct": 0,
        "Nov": 0,
        "Dec": 0
    }

    monthly_expense = {
        "Jan": 0,
        "Feb": 0,
        "Mar": 0,
        "Apr": 0,
        "May": 0,
        "Jun": 0,
        "Jul": 0,
        "Aug": 0,
        "Sep": 0,
        "Oct": 0,
        "Nov": 0,
        "Dec": 0
    }

    month_names = [
        "Jan", "Feb", "Mar", "Apr",
        "May", "Jun", "Jul", "Aug",
        "Sep", "Oct", "Nov", "Dec"
    ]

    # Calculate monthly income
    for income in incomes:

        try:

            month_number = int(str(income.date)[5:7])
            month_name = month_names[month_number - 1]

            monthly_income[month_name] += income.amount

        except (ValueError, TypeError, IndexError):

            pass

    # Calculate monthly expenses
    for expense in expenses:

        try:

            month_number = int(str(expense.date)[5:7])
            month_name = month_names[month_number - 1]

            monthly_expense[month_name] += expense.amount

        except (ValueError, TypeError, IndexError):

            pass

    # Recent transactions
    recent_transactions = []

    for income in incomes:

        recent_transactions.append({
            "type": "Income",
            "title": income.source,
            "amount": income.amount,
            "date": income.date
        })

    for expense in expenses:

        recent_transactions.append({
            "type": "Expense",
            "title": expense.category,
            "amount": expense.amount,
            "date": expense.date
        })

    recent_transactions.sort(
        key=lambda x: x["date"],
        reverse=True
    )

    return render_template(
        "dashboard.html",
        total_income=total_income,
        total_expense=total_expense,
        total_balance=total_balance,
        recent_transactions=recent_transactions[:5],
        monthly_income=monthly_income,
        monthly_expense=monthly_expense,
        budget_amount=budget_amount,
        budget_spent=budget_spent,
        budget_remaining=budget_remaining,
        budget_percentage=budget_percentage,
        selected_year=selected_year,
        selected_month_number=selected_month_number,
    )

@app.route("/add-income", methods=["GET", "POST"])
@login_required
def add_income():

    if request.method == "POST":

        source = request.form["source"]
        amount = float(request.form["amount"])
        date = request.form["date"]

        income = Income(
            source=source,
            amount=amount,
            date=date,
            user_id=current_user.id
        )

        db.session.add(income)
        db.session.commit()

        flash("Income added successfully!", "success")

        return redirect(url_for("dashboard"))

    return render_template("add_income.html")

@app.route("/add-expense", methods=["GET", "POST"])
@login_required
def add_expense():

    if request.method == "POST":

        category = request.form["category"]
        amount = float(request.form["amount"])
        date = request.form["date"]

        expense = Expense(
            category=category,
            amount=amount,
            date=date,
            user_id=current_user.id
        )

        db.session.add(expense)
        db.session.commit()

        flash("Expense added successfully!", "success")

        return redirect(url_for("dashboard"))

    return render_template("add_expense.html")

@app.route("/budget", methods=["GET", "POST"])
@login_required
def budget():

    if request.method == "POST":

        amount = float(request.form["amount"])
        budget_month = request.form["budget_month"]

        # Separate year and month
        year, month = map(int, budget_month.split("-"))

        # Check if a budget already exists for this month
        existing_budget = Budget.query.filter_by(
            user_id=current_user.id,
            month=month,
            year=year
        ).first()

        if existing_budget:

            # Update existing budget
            existing_budget.amount = amount

            flash(
                "Your budget has been updated successfully!",
                "success"
            )

        else:

            # Create a new budget
            new_budget = Budget(
                amount=amount,
                month=month,
                year=year,
                user_id=current_user.id
            )

            db.session.add(new_budget)

            flash(
                "Your monthly budget has been set successfully!",
                "success"
            )

        db.session.commit()

        return redirect(url_for("dashboard"))

    return render_template("budget.html")

@app.route("/expense-history")
@login_required
def expense_history():

    expenses = Expense.query.filter_by(user_id=current_user.id).all()

    return render_template(
        "expense_history.html",
        expenses=expenses
    )

@app.route("/income-history")
@login_required
def income_history():

    incomes = Income.query.filter_by(user_id=current_user.id).all()

    return render_template(
        "income_history.html",
        incomes=incomes
    )

@app.route("/transactions")
@login_required
def transactions():

    incomes = Income.query.filter_by(
        user_id=current_user.id
    ).all()

    expenses = Expense.query.filter_by(
        user_id=current_user.id
    ).all()

    transactions = []

    for income in incomes:
        transactions.append({
            "id": income.id,
            "type": "Income",
            "name": income.source,
            "amount": income.amount,
            "date": income.date
        })

    for expense in expenses:
        transactions.append({
            "id": expense.id,
            "type": "Expense",
            "name": expense.category,
            "amount": expense.amount,
            "date": expense.date
        })

    transactions.sort(
        key=lambda x: x["date"],
        reverse=True
    )

    return render_template(
        "transactions.html",
        transactions=transactions
    )

@app.route("/delete-income/<int:id>")
@login_required
def delete_income(id):

    income = Income.query.get_or_404(id)

    if income.user_id != current_user.id:
        flash("Unauthorized access!", "danger")
        return redirect(url_for("transactions"))

    db.session.delete(income)
    db.session.commit()

    flash("Income deleted successfully!", "success")

    return redirect(url_for("transactions"))


@app.route("/edit-income/<int:id>", methods=["GET", "POST"])
@login_required
def edit_income(id):

    income = Income.query.get_or_404(id)

    # Make sure the income belongs to the logged-in user
    if income.user_id != current_user.id:
        flash("Unauthorized access!", "danger")
        return redirect(url_for("transactions"))

    if request.method == "POST":

        income.source = request.form["source"]
        income.amount = float(request.form["amount"])
        income.date = request.form["date"]

        db.session.commit()

        flash("Income updated successfully!", "success")

        return redirect(url_for("transactions"))

    return render_template(
        "edit_income.html",
        income=income
    )

@app.route("/edit-expense/<int:id>", methods=["GET", "POST"])
@login_required
def edit_expense(id):

    expense = Expense.query.get_or_404(id)

    # Make sure the expense belongs to the logged-in user
    if expense.user_id != current_user.id:
        flash("Unauthorized access!", "danger")
        return redirect(url_for("transactions"))

    if request.method == "POST":

        expense.category = request.form["category"]
        expense.amount = float(request.form["amount"])
        expense.date = request.form["date"]

        db.session.commit()

        flash("Expense updated successfully!", "success")

        return redirect(url_for("transactions"))

    return render_template(
        "edit_expense.html",
        expense=expense
    )

@app.route("/delete-expense/<int:id>")
@login_required
def delete_expense(id):

    expense = Expense.query.get_or_404(id)

    if expense.user_id != current_user.id:
        flash("Unauthorized access!", "danger")
        return redirect(url_for("transactions"))

    db.session.delete(expense)
    db.session.commit()

    flash("Expense deleted successfully!", "success")

    return redirect(url_for("transactions"))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)