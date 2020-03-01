import re
from flask_wtf import Form, RecaptchaField
from wtforms import validators, StringField, PasswordField, TextAreaField
from models import User
from validators import check_bitcoin_address, check_unique


class RegisterForm(Form):
    login = StringField('Login name', [validators.Required(), validators.Length(4, 40),
                                       validators.Regexp(
                                           re.compile('^[a-z]+([-_]?[a-z0-9]+){0,2}$')), check_unique])

    password = PasswordField('Password', [
        validators.Required(), validators.Length(6, 255),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    email = StringField('Email', [validators.Required(), validators.Length(4, 40), validators.Email(), check_unique])
    bitcoin_wallet = StringField('Bitcoin Address', [validators.Required(), check_bitcoin_address, check_unique])
    captcha = RecaptchaField()


class LoginForm(Form):
    login = StringField('Login name', [validators.Required(), validators.Length(4, 40),
                                       validators.Regexp(
                                           re.compile('^[a-z]+([-_]?[a-z0-9]+){0,2}$'))])

    password = PasswordField('Password', [
        validators.Required(), validators.Length(6, 255)
    ])

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.user = None

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        user = User.objects(
            login=self.login.data).first()
        if user is None:
            self.login.errors.append('Unknown username')
            return False
        print user.password, self.password.data
        if not user.password == self.password.data:
            self.password.errors.append('Invalid password')
            return False

        self.user = user
        print 3
        return True

                                           
class FreeForm(Form):
    wallet = StringField('Wallet', [validators.Required(), check_bitcoin_address])


class ContactForm(Form):
    name = StringField('Name', [validators.Required(), validators.Length(4, 40),
                                validators.Regexp(
                                    re.compile('^[a-z]+([-_]?[a-z0-9]+){0,2}$'))])

    email = StringField('Email', [validators.Required(), validators.Length(4, 40), validators.Email()])

    message = TextAreaField('Message', [
        validators.Required(), validators.Length(6, 1024)])

