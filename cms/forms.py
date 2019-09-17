from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import SelectField,DateTimeField,StringField,PasswordField,SubmitField,BooleanField,TextAreaField
from wtforms.validators import ValidationError, DataRequired, Length, Email, EqualTo
from cms import  mongo
from flask_login import current_user

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    picture        = FileField('Profile Picture', validators=[DataRequired(),FileAllowed(['jpg','png'])])
    role = SelectField(u'User Type', choices=[(None, 'Select one'),('subscriber', 'Subscriber'),('admin', 'Admin'), ('author', 'Author')],validators=[DataRequired()])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = mongo.db.users.find_one({'username': username.data})
        if user:
            raise ValidationError('Username is taken.Please choose a diffrent one.')
        
    def validate_email(self, email):
        user=mongo.db.users.find_one({'email':email.data})
        if user:
            raise ValidationError('Email is taken.Please choose a diffrent one.')

class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class PostForm(FlaskForm):
    title =StringField('Title',
                           validators=[DataRequired(), Length(min=2, max=20)])
    content = TextAreaField('Content',
                        validators=[DataRequired()])
    submit = SubmitField('Post')

class UpdateForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture        = FileField('Profile Picture', validators=[FileAllowed(['jpg','png'])])
    submit = SubmitField('Update')
    
    
    def validate_username(self, username):
        identity= current_user._id
        user = mongo.db.users.find_one({'_id': identity})
        if username.data != user['username']:
            user = mongo.db.users.find_one({'username': username.data})
            if user:
                raise ValidationError('Username is taken.Please choose a diffrent one.')
        
    def validate_email(self, email):
        identity= current_user._id
        user = mongo.db.users.find_one({'_id': identity})
        if email.data != user['email']:
            user=mongo.db.users.find_one({'email':email.data})
            if user:
                raise ValidationError('Email is taken.Please choose a diffrent one.')

class FeedbackForm(FlaskForm):
    user=StringField('Your Username',
                           validators=[DataRequired(), Length(min=2)])
    feedback =TextAreaField('Feedback',
                           validators=[DataRequired(), Length(min=2)])
    submit = SubmitField('Send')                       
   



