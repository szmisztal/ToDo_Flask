from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField
from wtforms.validators import DataRequired

class TaskForm(FlaskForm):
    task_title = StringField("Title", validators = [DataRequired()])
    description = TextAreaField("Description")
    done = BooleanField("Done")
