from flask_wtf import FlaskForm
from wtforms import SelectField, TextAreaField, SelectMultipleField
from wtforms.validators import DataRequired, Optional


class SelectRepairForm(FlaskForm):
    color = SelectField(
        validators=[DataRequired()],
        coerce=int
    )

    repairs = SelectMultipleField(
        validators=[DataRequired()],
        coerce=int
    )

    problem_description = TextAreaField(
        validators=[Optional()]
    )

    def __init__(self, device, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.color.choices = [(color.id, color) for color in device.colors]
        self.repairs.choices = [(repair.id, repair) for repair in device.repairs]
