from flask import Blueprint, request, current_app, render_template, redirect, url_for, flash, make_response, jsonify
from db.db_connector import DBConnector

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

@admin.route('/ap/ticket/<int:ticket_id>', methods=['GET', 'POST'])
def ticket_detail(ticket_id):
    _ticket = None
    _ticket_index = None
    for index, ticket in enumerate(support_tickets):
        if ticket_id == ticket['id']:
            _ticket = ticket
            _ticket_index = index

    if request.method == 'POST':
        new_status = request.form.get('status')
        if new_status in ['in progress', 'resolved']:
            support_tickets[_ticket_index]['status'] = new_status
            message = f'Ticket status updated to "{new_status}"'
        else:
            message = 'Invalid status update'
        return redirect(url_for('admin.ticket_detail', ticket_id=ticket_id, message=message))

    return render_template('ticket_detail.html', ticket=_ticket)

@admin.route('/support/new-ticket', methods=['POST'])
def new_ticket():
    dbc = DBConnector()
    dict_data = request.get_json()
    if dict_data['token'] != current_app.config['ADMIN_AUTH_TOKEN'] and dict_data['token'] != current_app.config['AUTH_TOKEN']:
        new_ticket = {
            'id': len(support_tickets)+1,
            'user_id': dict_data['user_id'],
            'subject': dict_data['subject'],
            'status': dict_data['status'],
            'description': dict_data['description'],
        }
        ## add to db
        support_tickets.append(new_ticket)
        return jsonify({'status': 'Ok'}), 200
        # if result is True:
        #     return jsonify({'status': 'Ok'}), 200
        # else:
        #     return jsonify({'status': "Bad request"}), 400
