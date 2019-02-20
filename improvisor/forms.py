from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, IntegerField, validators, PasswordField


class FormTag(FlaskForm):
    tag = StringField('tag', [
        validators.DataRequired()
    ])
    
class FormSignup(FlaskForm):
    firstname = StringField('firstname', [
	    validators.Length(min=2, max=50),
		validators.Regexp('^\\w+$', message="First name may only contain letters")
		])
    lastname = StringField('lastname', [
        validators.Length(min=2, max=50),
		validators.Regexp('^\\w+$', message="Last name may only contain letters")
		])
    email = StringField('email', [validators.Email()
        ])
    password = PasswordField('password', [
		validators.DataRequired(),
		validators.Length(min=8, max=50)
		])

class FormAsset(FlaskForm):
    assetname = StringField('assetname', [
        validators.Length(min=2, max=200)
    ])
    tagname = StringField('tagname',[
        validators.Optional(True),
        validators.Length(min=2,max=200)
    ])


class FormLogin(FlaskForm):
    email = StringField('email', [validators.Email()])
    password = PasswordField('password', [
	    validators.DataRequired(),
		validators.Length(min=8, max=50)
	])