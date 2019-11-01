# =====================
# ALPACA MANAGEMENT API
# =====================

from flask import Flask, Blueprint, request, abort
from flask_restplus import Api, Resource, fields
import ASCOMErrors                                      # All Alpaca Devices

mgmt_blueprint = Blueprint('Management', __name__, 
                      url_prefix='/management',
                      static_folder='static')

#
# Set up the  Flask-RESTPlus api for Rotator and use the above 
# blueprint to establish the endpoint prefix.
#
api = Api(default='rotator', 
            default_label='<h2>ASCOM Alpaca Management API: Base URL = <tt>/management',
            contact='Bob Denny, DC-3 Dreams, SP',
            contact_email='rdenny@dc3.com',
            version='Exp. 1.0')

api.init_app(mgmt_blueprint, 
            version = '1.0',
            title='ASCOM Alpaca Management API', 
            description='<div><a href=\'https://ascom-standards.org/Developer/Alpaca.htm\' target=\'_new\'>'+
                '<img src=\'static/AlpacaLogo128.png\' align=\'right\' width=\'128\' height=\'101\' /></a>'+ 
                '<h2>This API enables Alpaca devices to be managed</h2>\r\n' +
                '<a href=\'https://ascom-standards.org/Developer/ASCOM%20Alpaca%20API%20Reference.pdf\' target=\'_new\'>' +
                    'View the ASCOM Alpaca API Reference (PDF)</a><br /><br />\r\n' + 
                '<a href=\'https://ascom-standards.org/api/?urls.primaryName=ASCOM%20Alpaca%20Management%20API\' target=\'_new\'>' +
                'Try out the live ASCOM Alpaca Management API (Swagger)</a><br /><br /></div>')

