from flask import Blueprint, request, current_app, render_template, redirect, url_for, flash, make_response, jsonify
from db.db_connector import DBConnector
import json
admin = Blueprint('admin', __name__, template_folder='templates')

### temporary Fake DB to speed up development
tmp_db = [
    {'ap_user_1':'ap_password_1'},
    {'ap_user_2':'ap_password_2'},
    {'ap_user_3':'ap_password_3'}
]

support_tickets = [
    {
        "id": 1,
        "user_id": 1,
        "subject": 'Error',
        "status": "waiting for support",
        "description": "Hello isctespot support, I am having issue when downloading the invoince. Can you please fix it, it is urgent!"
    },
    {
        "id": 3,
        "user_id": 1,
        "subject": 'Feature Request',
        "status": "waiting for support",
        "description": "Hello I have a feature request! Can you please allow the company admins to edit the style of"
    }
]
###
@admin.route('/ap/login', methods=['GET', 'POST'])
def login():
    print(f'Login functoion!')
    print(f'Request data: {request.get_data()}')
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        print(f'Username: {username}, password: {password}')
        for user in tmp_db:
            if user[username] == password:
                print('User found')
                response = redirect(url_for('admin.view_tickets'))
                session_token = current_app.config.get("AP_AUTH_TOKEN", "default_token")
                response.set_cookie('session_token', session_token)
                return response

        flash('Invalid username or password', 'danger')
    return render_template('login.html')

@admin.route('/ap/logout')
def logout():
    response = make_response(redirect(url_for('admin.login')))
    response.set_cookie('session_token', '', expires=0)
    return response

@admin.route('/ap/tickets')
def view_tickets():
    tickets = support_tickets
    return render_template('tickets.html', tickets=tickets)

@admin.route('/support/ticket/<int:ticket_id>', methods=['GET', 'POST'])
def ticket_detail(ticket_id):
    dbc = DBConnector()
    dict_data = request.get_json()
    result = dbc.execute_query('get_ticket_by_id', args=ticket_id)
    if result['UserID'] != dict_data['user_id']:
        return jsonify({'status': "Unauthorized"}), 403
    else:
        return jsonify({'status': 'Ok', 'ticket':result}), 200
    

@admin.route('/support/new-ticket', methods=['POST'])
def new_ticket():
    dbc = DBConnector()
    dict_data = request.get_json()
    if dict_data['category'] not in ['Technical Issue', 'Billing', 'Question', 'Feature Request']:
        return jsonify({'status': "Bad request"}), 400
    if dict_data['token'] != current_app.config['ADMIN_AUTH_TOKEN'] and dict_data['token'] != current_app.config['AUTH_TOKEN']:
        return jsonify({'status': "Unauthorized"}), 403
    ticket = {
        'user_id': dict_data['user_id'],
        'category': dict_data['category'],
        'status': dict_data['status'],
        'description': dict_data['description'],
        'messages': json.dumps([])
    }
    result = dbc.execute_query('create_ticket', args=ticket)
    if isinstance(result, int):
        return jsonify({'status': 'Ok', 'ticket_id':result}), 200
    else:
        return jsonify({'status': 'Bad reuest'}), 400

@admin.route('/support/tickets', methods=['POST'])
def tickets():
    dbc = DBConnector()
    dict_data = request.get_json()
    results = None
    if dict_data['token'] == current_app.config['ADMIN_AUTH_TOKEN'] or dict_data['token'] == current_app.config['AUTH_TOKEN']:
        if dict_data['token'] == current_app.config['AUTH_TOKEN']:
            results = dbc.execute_query('get_user_tickets', args=dict_data['user_id'])
        if dict_data['token'] == current_app.config['ADMIN_AUTH_TOKEN']:
            results = dbc.execute_query('get_admin_tickets', args=dict_data['company_id'])
        if isinstance(results, list):
            return jsonify({'status': 'Ok', 'tickets': results}), 200
        return jsonify({'status': 'Bad request'}), 400

    return jsonify({'status': 'Unauthorized'}), 403

@admin.route("/support/ticket/<int:ticket_id>/new-message", methods=['POST'])
def new_message(ticket_id):
    dbc = DBConnector()
    dict_data = request.get_json()
    result = dbc.execute_query('get_ticket_by_id', args=ticket_id)
    if result['UserID'] != dict_data['user_id']:
        return jsonify({'status': "Unauthorized"}), 403
    user = dbc.execute_query('get_user_by_id', args=result['UserID'])
    result = dbc.execute_query('update_ticket_messages', args={
        "username": user['Username'],
        "ticket_id": ticket_id,
        "message": dict_data['message'],
        'is_agent': False # TODO dinamico (check if is agent by userID)
    })
    if result:
        return jsonify({'status': 'Ok'}), 200
    else:
        return jsonify({'status': 'Bad request'}), 400
