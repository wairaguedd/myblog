from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from models import User, Category, Tag

class LoginForm(FlaskForm):
    """Form for user login."""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class PostForm(FlaskForm):
    """Form for creating and editing blog posts."""
    title = StringField('Title', validators=[DataRequired(), Length(min=1, max=200)])
    slug = StringField('Slug', validators=[DataRequired(), Length(min=1, max=200)])
    content = TextAreaField('Content', validators=[DataRequired()])
    excerpt = TextAreaField('Excerpt', validators=[Length(max=300)])
    category_id = SelectField('Category', coerce=int)
    tags = StringField('Tags (comma separated)', validators=[Length(max=200)])
    published = BooleanField('Published')
    submit = SubmitField('Save Post')
    
    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.category_id.choices = [(c.id, c.name) for c in Category.query.order_by(Category.name).all()]
        # Add a "No Category" option
        self.category_id.choices.insert(0, (0, 'No Category'))

class CategoryForm(FlaskForm):
    """Form for creating and editing categories."""
    name = StringField('Name', validators=[DataRequired(), Length(min=1, max=50)])
    slug = StringField('Slug', validators=[DataRequired(), Length(min=1, max=50)])
    submit = SubmitField('Save Category')

class TagForm(FlaskForm):
    """Form for creating and editing tags."""
    name = StringField('Name', validators=[DataRequired(), Length(min=1, max=50)])
    slug = StringField('Slug', validators=[DataRequired(), Length(min=1, max=50)])
    submit = SubmitField('Save Tag')

class CommentForm(FlaskForm):
    """Form for adding comments to blog posts."""
    name = StringField('Name', validators=[DataRequired(), Length(min=1, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(min=1, max=100)])
    content = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Add Comment')

class ContactForm(FlaskForm):
    """Form for the contact page."""
    name = StringField('Name', validators=[DataRequired(), Length(min=1, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(min=1, max=100)])
    subject = StringField('Subject', validators=[DataRequired(), Length(min=1, max=200)])
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send Message')

class SearchForm(FlaskForm):
    """Form for searching blog posts."""
    query = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Search')
