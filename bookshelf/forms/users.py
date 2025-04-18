from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import Length, URL, Optional

class ProfileForm(FlaskForm):
    bio = TextAreaField('Bio', validators=[
        Optional(),
        Length(max=500, message='Bio must be less than 500 characters.')
    ])
    profile_pic_url = StringField('Profile Picture URL', validators=[
        Optional(),
        URL(message='Must be a valid URL.')
    ])
    submit = SubmitField('Update Profile') 