# Testing WT Forms MVC.
#
import os
from flask import Flask, request, abort,  render_template, flash
from flask_wtf import FlaskForm
from wtforms import Form, BooleanField, IntegerField, FloatField, validators, SubmitField

# MVC MODEL

class SetupForm(FlaskForm):

    can_reverse =   BooleanField(label='Can Reverse', 
                        description='True if the rotator\'s direction should be clockwise.')

    step_size =     FloatField(label='Step size (deg.)', 
                        description='Angular resolution of the rotator, fractional degrees per step',
                        validators=[validators.InputRequired('Step size must not be empty'),
                                    validators.NumberRange(min=0.1, max=5.0, message='Step size must be between %(min)s and %(max)s deg')])

    steps_sec =     IntegerField(label = 'Steps per sec.', 
                        description='Angular rotation rate in whole steps per second',
                        validators=[validators.InputRequired('Step per sec. must not be empty'),
                                    validators.NumberRange(min=5, max=60, message='Steps per sec. must be between %(min)s and %(max)s')])

    update =        SubmitField('Update')

# SERVER

app = Flask(__name__, static_url_path='', static_folder='static', template_folder='templates')
# needed for session (flash queue uses this), CSRF protection
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

# DATA (NOT PERSISTED)

class Rotator:
    can_reverse = False
    step_size = 0.5
    steps_per_sec = 20

R = Rotator()

# MVC VIEW FUNCTION

@app.route('/setup', methods=['GET', 'POST'])
def setup():
    setup_form = SetupForm()                            # FLaskForm auto-loads the form from a POST
    if setup_form.validate_on_submit():
        R.can_reverse = setup_form.can_reverse.data
        R.step_size = setup_form.step_size.data
        R.steps_per_sec = setup_form.steps_sec.data
        flash('Settings successfully updated')

    setup_form.can_reverse.data = R.can_reverse
    setup_form.step_size.data = R.step_size
    setup_form.steps_sec.data = R.steps_per_sec

    return render_template('/setup.html', 
                form=setup_form, 
                template='form_page',
                title='Rotator Simulator Setup Form')

# STARTUP

app.run('127.0.0.1', 5555)
