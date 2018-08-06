from LoginDemoApp import app, db, bcrypt, serializer, mail
from LoginDemoApp.database_tables import User
from LoginDemoApp.forms import RegistrationForm, LoginForm
from flask import render_template, url_for, flash, Markup, redirect, request
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from itsdangerous import SignatureExpired, BadTimeSignature


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')


@app.route("/signUp", methods=['GET', 'POST'])
def sign_up():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Extract user inputs
        username = form.username.data.lower()
        email = form.email.data.lower()
        password = form.password.data

        # Hash password
        password = bcrypt.generate_password_hash(password)

        # Store user inputs in database
        user = User(username=username, email=email, password=password, email_confirmed=False)
        db.session.add(user)
        db.session.commit()

        # Redirect to send_email route to send confirmation mail
        return redirect(url_for('send_email', token=serializer.dumps(email, salt='email')))
    return render_template('sign_up.html', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    # If user is already logged in redirect to home page
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    # Create LoginForm() object to validate user input when its submitted as a POST request
    form = LoginForm()

    # If user input has been submitted and been validated log the user in
    if form.validate_on_submit():
        # Extract user inputs
        email = form.email.data.lower()
        password = form.password.data

        # Search for user in database
        user = User.query.filter_by(email=email).first()

        # If user has been found, the password matches and users email has been confirmed, log user in
        if user and bcrypt.check_password_hash(user.password, password) and user.email_confirmed:
            login_user(user, remember=form.remember.data)

            # If login is being accessed from a redirect store target page in variable called next_page
            next_page = request.args.get('next')

            # Redirect to target page or home page based on how user got to the login page
            return redirect(next_page) if next_page else redirect(url_for('home'))

        # If email has not been confirmed yet offer user to resend confirmation mail
        elif user and bcrypt.check_password_hash(user.password, password) and not user.email_confirmed:
            flash(Markup('Please confirm your email address first <a href="%s">(Resend Email)</a>' % url_for('send_email', token=serializer.dumps(email, salt='email'))))

        # Otherwise the user must have entered wrong credentials
        else:
            flash('Login failed. Please check your credentials')

    # If user is not already logged in redirect to login page
    return render_template('login.html', form=form)


# This route can only be accessed if user is already logged in
@login_required
@app.route("/logout")
def logout():
    # Log out user and redirect to home page
    logout_user()
    return redirect(url_for('home'))


# This route can only be accessed with a valid token
# When accessed it confirms the email the token is associated with
@app.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        # Extract email address from token
        email = serializer.loads(token, salt='email', max_age=1800)

        # Update confirmed email flag to true
        user = User.query.filter_by(email=email).first()
        user.email_confirmed = True
        db.session.add(user)
        db.session.commit()

        # Notify user with success message
        flash('Your account has been created! You are now able to log in')

    # If token is expired or invalid notify user
    except (SignatureExpired, BadTimeSignature):
        if SignatureExpired:
            return 'Token expired'
        elif BadTimeSignature:
            return 'Invalid token'

    # If email confirmation was successful return to login page so user can login
    return redirect(url_for('login'))


# This route is accessed whenever a confirmation mail need to be send
# Instead of an email a token of the mail is being passed to the URL, to make brute force attacks more difficult
@app.route('/send_mail/<token>')
def send_email(token):

    # Extract email address from token
    email = serializer.loads(token, salt='email', max_age=1800)

    # Send confirmation mail to extracted email address
    token = serializer.dumps(email, salt='email')

    # Email head message
    msg = Message('FlaskLoginDemo.PythonAnywhere.com -- Confirm your email', sender='textspace.confirm@gmail.com', recipients=[email])

    # Email body message
    msg.body = '''Please click this link to confirm your email: %s 
    If you did not make this request simply ignore this email.''' \
               % url_for('confirm_email', token=token, _external=True)

    # Send email
    mail.send(msg)

    # Notify user that email has been send
    flash_msg = 'A confirmation email has been send to %s. Please follow its instructions to login. <a href="%s">' \
                '(Resend Email)</a>' % (email, url_for('send_email', token=serializer.dumps(email, salt='email')))

    flash(Markup(flash_msg))

    # Redirect to login page
    return redirect(url_for('login'))
