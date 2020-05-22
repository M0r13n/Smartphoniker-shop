import typing

from flask_wtf import FlaskForm
from wtforms import SelectField, TextAreaField, SelectMultipleField, StringField, BooleanField, SubmitField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Length, Email

from project.server.models import Color, Repair, Shop


class SelectRepairForm(FlaskForm):
    color = SelectField(
        validators=[DataRequired("Dieses Feld wird benötigt")],
        coerce=int
    )

    repairs = SelectMultipleField(
        validators=[DataRequired("Dieses Feld wird benötigt")],
        coerce=int
    )

    problem_description = TextAreaField(
        validators=[]
    )

    def __init__(self, device, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.color.choices = [(color.id, color) for color in device.colors]
        self.repairs.choices = [(repair.id, repair) for repair in device.repairs]

    def get_color(self) -> typing.Optional[Color]:
        return Color.query.get_or_404(self.color.data)

    def get_repairs(self) -> typing.List[Repair]:
        return list(map(lambda repair_id: Repair.query.get_or_404(repair_id), self.repairs.data))


class RegisterCustomerForm(FlaskForm):
    first_name = StringField(
        "Vorname",
        validators=[
            DataRequired("Dieses Feld wird benötigt"),
            Length(min=1, max=255, message="Der Name muss zwischen 1 und 255 Zeichen lang sein")
        ]
    )

    last_name = StringField(
        "Nachname",
        validators=[
            DataRequired("Dieses Feld wird benötigt"),
            Length(min=1, max=255, message="Der Name muss zwischen 1 und 255 Zeichen lang sein")
        ]
    )

    street = StringField(
        "Straße",
        validators=[
            DataRequired("Dieses Feld wird benötigt"),
            Length(min=1, max=255, message="Die Straße muss zwischen 1 und 255 Zeichen lang sein")
        ]
    )

    zip_code = StringField(
        "PLZ",
        validators=[
            DataRequired("Dieses Feld wird benötigt"),
            Length(min=3, max=10, message="Die PLZ muss zwischen 3 und 10 Zeichen lang sein")
        ]
    )

    city = StringField(
        "Stadt",
        validators=[
            DataRequired("Dieses Feld wird benötigt"),
            Length(min=1, max=255, message="Die Stadt muss zwischen 1 und 255 Zeichen lang sein")
        ]
    )

    email = EmailField(
        "Email",
        validators=[
            DataRequired("Dieses Feld wird benötigt"),
            Email(message="Bitte gib eine gültige Email Adresse an"),
            Length(min=1, max=64, message="Die Email muss zwischen 1 und 255 Zeichen lang sein")
        ]
    )

    tel = StringField(
        "Telefon",
        validators=[
            Length(min=0, max=64, message="Die Nummer muss zwischen 3 und 64 Zeichen lang sein")
        ]
    )

    tricoma_id = StringField(
        "Kundennummer",
        validators=[
            Length(min=0, max=64, message="Die Nummer muss zwischen 1 und 64 Zeichen lang sein")
        ]
    )


class FinalSubmitForm(FlaskForm):
    shipping_label = BooleanField(
        "Versandlabel",
        default=False
    )

    kva_button = SubmitField(
        "kostenloser Kostenvoranschlag",
        validators=[],
        default=False
    )

    shop = QuerySelectField(
        "Shop",
        query_factory=lambda: Shop.query.all(),
        get_pk=lambda x: x.id,
        get_label=lambda x: x.name,
        validators=[DataRequired("Bitte wähle den Zielshop.")]
    )
