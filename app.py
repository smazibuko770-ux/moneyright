from flask import Flask, render_template, request, redirect, session, Response
from supabase import create_client, Client
from datetime import datetime

app = Flask(__name__)
app.secret_key = "Mazibuko1"

SUPABASE_URL = "https://zcwpkbetdtpzgtmqjzxa.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inpjd3BrYmV0ZHRwemd0bXFqenhhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzYzODc4MDQsImV4cCI6MjA5MTk2MzgwNH0.I_BO0Mb0IwFMmJu1TwjmLTjzSkICtMkVexpgQv_hAak"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# HOME


@app.route('/')
def home():
    if 'user' not in session:
        return redirect('/login')

    user_id = session['user']

    earnings_data = supabase.table("earnings").select(
        "*").eq("user_id", user_id).execute()
    expenses_data = supabase.table("expenses").select(
        "*").eq("user_id", user_id).execute()

    earnings = [{
        "amount": float(e["amount"]),
        "date": e["created_at"][:10]
    } for e in earnings_data.data]

    expenses = [{
        "amount": float(e["amount"]),
        "date": e["created_at"][:10]
    } for e in expenses_data.data]

    total_earnings = sum(e["amount"] for e in earnings)
    total_expenses = sum(e["amount"] for e in expenses)
    profit = total_earnings - total_expenses

    return render_template(
        'index.html',
        earnings=earnings,
        expenses=expenses,
        total_earnings=total_earnings,
        total_expenses=total_expenses,
        profit=profit
    )

# LOGIN


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        res = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        if res.user:
            session['user'] = res.user.id
            return redirect('/')

    return render_template('login.html')

# REGISTER


@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ""

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        supabase.auth.sign_up({
            "email": email,
            "password": password
        })

        message = "Registration successful"

    return render_template('register.html', message=message)

# LOGOUT


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# ADD EARNING


@app.route('/add_earning', methods=['GET', 'POST'])
def add_earning():
    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':
        amount = float(request.form['amount'])

        supabase.table("earnings").insert({
            "amount": amount,
            "user_id": session['user'],
            "created_at": datetime.utcnow().isoformat()
        }).execute()

        return redirect('/')

    return render_template('add_earning.html')

# ADD EXPENSE


@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':
        amount = float(request.form['amount'])

        supabase.table("expenses").insert({
            "amount": amount,
            "user_id": session['user'],
            "created_at": datetime.utcnow().isoformat()
        }).execute()

        return redirect('/')

    return render_template('add_expense.html')

# DOWNLOAD REPORT


@app.route('/download')
def download():
    if 'user' not in session:
        return redirect('/login')

    user_id = session['user']

    earnings_data = supabase.table("earnings").select(
        "*").eq("user_id", user_id).execute()
    expenses_data = supabase.table("expenses").select(
        "*").eq("user_id", user_id).execute()

    report = "MoneyRight Report\n\n"

    report += "EARNINGS:\n"
    for e in earnings_data.data:
        report += f"R{e['amount']} - {e['created_at'][:10]}\n"

    report += "\nEXPENSES:\n"
    for e in expenses_data.data:
        report += f"R{e['amount']} - {e['created_at'][:10]}\n"

    return Response(
        report,
        mimetype="text/plain",
        headers={"Content-Disposition": "attachment;filename=report.txt"}
    )

# RESET


@app.route('/reset', methods=['POST'])
def reset():
    if 'user' not in session:
        return redirect('/login')

    user_id = session['user']

    supabase.table("earnings").delete().eq("user_id", user_id).execute()
    supabase.table("expenses").delete().eq("user_id", user_id).execute()

    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
