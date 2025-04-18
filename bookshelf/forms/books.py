from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, TextAreaField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, Optional, NumberRange

class BookSearchForm(FlaskForm):
    """Form for searching books"""
    search = StringField('Search')
    genre = SelectField('Genre', coerce=int, validators=[Optional()])
    submit = SubmitField('Search')
    
    def __init__(self, *args, **kwargs):
        super(BookSearchForm, self).__init__(*args, **kwargs)
        # Genre choices will be populated in the route

class ReviewForm(FlaskForm):
    """Form for book reviews"""
    rating = SelectField('Rating', coerce=int, 
                        choices=[(1, '1 Star'), (2, '2 Stars'), (3, '3 Stars'), 
                                 (4, '4 Stars'), (5, '5 Stars')],
                        validators=[DataRequired()])
    text = TextAreaField('Review', validators=[
        DataRequired(),
        Length(min=10, max=2000, message='Review must be between 10 and 2000 characters.')
    ])
    submit = SubmitField('Submit Review')

class BookFileUploadForm(FlaskForm):
    """Form for uploading book files"""
    file = FileField('Select File', validators=[
        FileRequired(),
        FileAllowed(['pdf', 'epub', 'mobi', 'txt', 'doc', 'docx'], 
                   'Only PDF, EPUB, MOBI, TXT, DOC, and DOCX files are allowed.')
    ])
    book = SelectField('Link to Book (Optional)', coerce=int, validators=[Optional()])
    description = TextAreaField('Description', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Upload File') 