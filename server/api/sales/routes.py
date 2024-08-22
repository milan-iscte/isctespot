from flask import Flask, Blueprint, request, jsonify, current_app
from db.db_connector import DBConnector
import json

sales = Blueprint('sales', __name__)

@sales.route('/user/overview', methods=['GET', 'POST'])
def list_user_sales():
    ''' List user sales function'''
    dbc = DBConnector()
    dict_data = request.get_json()
    if dict_data['token'] != current_app.config['ADMIN_AUTH_TOKEN'] and dict_data['token'] != current_app.config['AUTH_TOKEN']:
        return jsonify({'status': 'Unauthorised'}), 403
    results = dbc.execute_query(query='get_user_sales', args=dict_data['user_id'])
    if isinstance(results, list):
        return jsonify({'status': 'Ok', 'sales': results}), 200
    return jsonify({'status': 'Bad request'}), 400

@sales.route('/sales/new', methods=['POST'])
def add_new_sale():
    ''' Add new sale function '''
    dbc = DBConnector()
    dict_data = request.get_json()
    if dict_data['token'] != current_app.config['ADMIN_AUTH_TOKEN'] and dict_data['token'] != current_app.config['AUTH_TOKEN']:
        return jsonify({'status': 'Unauthorised'}), 403
    result = dbc.execute_query(query='create_sale', args={
        'client_id': dict_data['client_id'],
        'user_id': dict_data['user_id'],
        'product': dict_data['product'],
        'price': dict_data['price'],
        'quantity': dict_data['quantity']
    })
    if isinstance(result, int):
        return jsonify({'status': 'Ok', 'sale_id': result}), 200
    return jsonify({'status': 'Bad request'}), 400