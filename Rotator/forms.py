#
# In keeping with MVC we'll separate the logic for the setup form into this model
# NOTE: Ues the thin wrapper/helper Flask-WTF. Recommended for CSRF protection 
# and convenience/simplification running WTF in Flask.

from wtforms import Form, BooleanField, IntegerField, FloatField, SubmitField, SelectField, validators
from wtforms.validators import ValidationError, DataRequired, NumberRange
from flask_wtf import FlaskForm     # *** NOTE THIS ***
import RotatorAPI

class DevSetupForm(FlaskForm):

    reverse =       BooleanField(label='Reverse', 
                        description='True if the rotator\'s direction should be clockwise.')

    step_size =     FloatField(label='Step size (deg.)', 
                        description='Angular resolution of the rotator, fractional degrees per step',
                        validators=[DataRequired('Step size must not be empty'),
                                    NumberRange(min=0.1, max=5.0, message='Step size must be between 0.1 and 5.0 deg')])

    steps_sec =     IntegerField(label = 'Steps per sec.', 
                        description='Angular rotation rate in whole steps per second',
                        validators=[DataRequired('Step per sec. must not be empty'),
                                    NumberRange(min=1, max=60, message='Steps per sec. must be between 1 and 60')])

    update =        SubmitField('Update')

class SvrSetupForm(FlaskForm):
    nothing = ''