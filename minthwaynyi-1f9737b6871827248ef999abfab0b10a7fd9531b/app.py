import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///moneytracker.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    # Retrieve data from the ledger table (newest first)
    transactions = db.execute(
        "SELECT * FROM ledger WHERE user_id = ? ORDER BY id DESC", session["user_id"]
    )

    # Format the date
    for transaction in transactions:
        transaction["date"] = transaction["date"][:10]

    # Calculate total earnings
    result_earning = db.execute(
        "SELECT SUM(amount) FROM ledger WHERE user_id = ? AND type = 'earning'",
        session["user_id"],
    )
    total_earning = (
        float(result_earning[0]["SUM(amount)"])
        if result_earning[0]["SUM(amount)"]
        else 0.0
    )

    # Calculate total spendings
    result_spending = db.execute(
        "SELECT SUM(amount) FROM ledger WHERE user_id = ? AND type = 'spending'",
        session["user_id"],
    )
    total_spending = (
        float(result_spending[0]["SUM(amount)"])
        if result_spending[0]["SUM(amount)"]
        else 0.0
    )

    # Calculate the difference
    net_amount = total_earning - total_spending

    # Count the number of different months in the ledger
    distinct_months = len(set(transaction["date"][:7] for transaction in transactions))

    # Calculate monthly averages
    average_earning = round(total_earning / distinct_months, 2) if distinct_months > 0 else 0.0
    average_spending = round(total_spending / distinct_months, 2) if distinct_months > 0 else 0.0
    average_net = round(net_amount / distinct_months, 2) if distinct_months > 0 else 0.0

    return render_template(
        "index.html",
        transactions=transactions,
        total_earning=total_earning,
        total_spending=total_spending,
        net_amount=net_amount,
        average_earning=average_earning,
        average_spending=average_spending,
        average_net=average_net,
    )


@app.route("/new", methods=["GET", "POST"])
@login_required
def new():
    tags = db.execute(
        "SELECT DISTINCT tag FROM ledger WHERE user_id = ?", session["user_id"]
    )

    if request.method == "POST":
        # Get form data
        amount = float(request.form.get("amount"))
        transaction_type = request.form.get("type")
        reason = request.form.get("reason")
        date_str = request.form.get("date")
        date_obj = datetime.strptime(
            date_str, "%Y-%m-%d"
        )  # Convert date from string to datetime
        tag = request.form.get("tag")
        user_id = session["user_id"]

        # Insert data into the ledger table
        db.execute(
            "INSERT INTO ledger (amount, type, reason, date, tag, user_id) VALUES (?, ?, ?, ?, ?, ?)",
            amount,
            transaction_type,
            reason,
            date_obj,
            tag,
            user_id,
        )

        # Redirect to the index page after the form is submitted
        return redirect("/")
    else:
        return render_template("new.html", tags=tags)


@app.route("/edit/<int:transaction_id>", methods=["GET", "POST"])
@login_required
def edit(transaction_id):
    tags = db.execute(
        "SELECT DISTINCT tag FROM ledger WHERE user_id = ?", session["user_id"]
    )

    if request.method == "POST":
        # Get form data
        amount = float(request.form.get("amount"))
        transaction_type = request.form.get("type")
        reason = request.form.get("reason")
        date_str = request.form.get("date")
        date_obj = datetime.strptime(
            date_str, "%Y-%m-%d"
        )  # Convert date from string to datetime
        tag = request.form.get("tag")

        # Update the database with the new data
        db.execute(
            "UPDATE ledger SET amount=?, type=?, reason=?, date=?, tag=? WHERE id=?",
            amount,
            transaction_type,
            reason,
            date_obj,
            tag,
            transaction_id,
        )

        flash("Transaction updated successfully", "success")
        return redirect("/")

    else:
        # Retrieve the transaction data from the database
        transaction = db.execute("SELECT * FROM ledger WHERE id = ?", transaction_id)[0]

        # Format the date
        transaction["date"] = transaction["date"][:10]

        return render_template("edit.html", tags=tags, transaction=transaction)


@app.route("/delete/<int:transaction_id>", methods=["GET", "POST"])
@login_required
def delete(transaction_id):
    if request.method == "POST":
        # Delete the transaction from the database
        db.execute("DELETE FROM ledger WHERE id = ?", transaction_id)
        flash("Transaction deleted successfully", "success")
        return redirect("/")
    else:
        return render_template("delete.html")


@app.route("/filter", methods=["GET", "POST"])
@login_required
def filter_transactions():
    tags = db.execute(
        "SELECT DISTINCT tag FROM ledger WHERE user_id = ?", session["user_id"]
    )

    if request.method == "POST":
        # Retrieve form data
        limit = request.form.get("limit")
        amount_str = request.form.get("amount")
        transaction_type = request.form.get("type")
        reason = request.form.get("reason")
        date1 = request.form.get("date1")
        date2 = request.form.get("date2")
        tag = request.form.get("tag")

        # Construct the SQL query based on form data
        sql_query = "SELECT * FROM ledger WHERE user_id = ?"
        params = [session["user_id"]]

        if limit == "above" and amount_str:
            sql_query += " AND amount > ?"
            params.append(float(amount_str))

        elif limit == "below" and amount_str:
            sql_query += " AND amount < ?"
            params.append(float(amount_str))

        if transaction_type and transaction_type != "both":
            sql_query += " AND type = ?"
            params.append(transaction_type)

        if reason:
            sql_query += " AND reason LIKE ?"
            params.append(f"%{reason}%")

        if date1 and date2:
            sql_query += " AND date BETWEEN ? AND ?"
            params.extend([date1, date2])

        if tag:
            sql_query += " AND tag = ?"
            params.append(tag)

        # Execute the SQL query with parameters
        filtered_transactions = db.execute(sql_query, *params)

        # Format the date
        for transaction in filtered_transactions:
            transaction["date"] = transaction["date"][:10]

        # Calculate totals for the filtered transactions
        total_earning = sum(
            float(transaction["amount"])
            for transaction in filtered_transactions
            if transaction["type"] == "earning"
        )
        total_spending = sum(
            float(transaction["amount"])
            for transaction in filtered_transactions
            if transaction["type"] == "spending"
        )
        net_amount = total_earning - total_spending

        # Render the results in the filtered.html template
        return render_template(
            "filtered.html",
            transactions=filtered_transactions,
            total_earning=total_earning,
            total_spending=total_spending,
            net_amount=net_amount,
        )

    else:
        # Render the form on GET request
        return render_template("filter.html", tags=tags)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout", methods=["GET", "POST"])
def logout():
    """Log user out"""
    if request.method == "POST":
        # Forget any user_id
        session.clear()

        # Redirect user to login form
        return redirect("/")

    # Display confirmation page for GET request
    return render_template("logout.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # Ensure password verification was submitted
        elif not request.form.get("verification"):
            return apology("must provide password verification")

        # Ensure password was confirmed accurately
        elif request.form.get("password") != request.form.get("verification"):
            return apology("passwords need to be identical")

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if rows:
            return apology("this username has already been taken")

        # Register the user in database
        db.execute(
            "INSERT INTO users (username, hash) VAlUES(?, ?)",
            request.form.get("username"),
            generate_password_hash(request.form.get("password")),
        )

        # Query database for the current user
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("signup.html")


@app.route("/username", methods=["GET", "POST"])
@login_required
def change_username():
    """Change user username"""
    if request.method == "POST":
        # Ensure new username was submitted
        new_username = request.form.get("new_username")
        if not new_username:
            return apology("must provide new username")

        # Query database for the current user
        rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])

        # Check if the new username is the same as the current one
        if new_username == rows[0]["username"]:
            return apology("new username must be different")

        # Query database for the new username
        rows = db.execute("SELECT * FROM users WHERE username = ?", new_username)
        if rows:
            return apology(
                "this username is already taken, please choose a different one"
            )

        # Update the username
        db.execute(
            "UPDATE users SET username = ? WHERE id = ?",
            new_username,
            session["user_id"],
        )

        flash("Username has been changed successfully!")
        return redirect("/")

    else:
        rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        current_username = rows[0]["username"]

        return render_template("username.html", current_username=current_username)


@app.route("/password", methods=["GET", "POST"])
@login_required
def change_password():
    """Change user password"""
    if request.method == "POST":
        # Ensure old password was submitted
        if not request.form.get("old_password"):
            return apology("must provide old password")

        # Ensure new password was submitted
        elif not request.form.get("new_password"):
            return apology("must provide new password")

        # Ensure new password verification was submitted
        elif not request.form.get("verification"):
            return apology("must provide password verification")

        # Ensure new password is confirmed accurately
        elif request.form.get("new_password") != request.form.get("verification"):
            return apology("new passwords need to be identical")

        # Query database for the current user
        rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])

        # Ensure old password is correct
        if not check_password_hash(rows[0]["hash"], request.form.get("old_password")):
            return apology("invalid old password")

        # Update the password
        db.execute(
            "UPDATE users SET hash = ? WHERE id = ?",
            generate_password_hash(request.form.get("new_password")),
            session["user_id"],
        )

        flash("Password has been changed successfully!")
        return redirect("/")

    else:
        return render_template("password.html")
