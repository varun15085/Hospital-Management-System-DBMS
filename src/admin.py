from flask import render_template, Blueprint, flash, redirect, url_for, request
from flask_login import login_required, current_user
from . import requires_access_level, mysql
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from .forms import *
from .models import DE_Operator,Doctor,FD_Operator,Administrator, identify_class

adm = Blueprint('adm', __name__)

@adm.route('/admin', methods = ['GET', 'POST'])
@adm.route('/admin/', methods = ['GET', 'POST'])
@login_required
@requires_access_level(1)
def admin():
    cur = mysql.connection.cursor()
    cur.execute("SELECT Doctor_ID, Name, Address, Age, Gender, Personal_Contact FROM Doctor ORDER BY Doctor_ID LIMIT 5")
    doctors = cur.fetchall()
    cur.execute("SELECT FD_Operator_ID, Name, Address, Age, Gender, Personal_Contact FROM FD_Operator ORDER BY FD_Operator_ID LIMIT 5")
    fdos = cur.fetchall()
    cur.execute("SELECT DE_Operator_ID, Name, Address, Age, Gender, Personal_Contact FROM DE_Operator ORDER BY DE_Operator_ID LIMIT 5")
    deos = cur.fetchall()
    return render_template('admin_dashboard.html', total_doctors=len(doctors), total_fdo=len(fdos), total_deo=len(deos), doctors=doctors, fdos=fdos, deos=deos, user=current_user)

@adm.route('/admin/edit_user', methods=['GET', 'POST'])
@adm.route('/admin/edit_user/', methods=['GET', 'POST'])
@login_required
@requires_access_level(1)
def admin_get_user():
    form = GetUser()
    if form.validate_on_submit():
        user_type = form.users.data
        return redirect(url_for('adm.admin_edit_user', user_type=user_type, user=current_user))
    return render_template('admin_select_user.html', form=form, user=current_user)

@adm.route('/admin/edit_user/<user_type>', methods=['GET', 'POST'])
@adm.route('/admin/edit_user/<user_type>/', methods=['GET', 'POST'])
@login_required
@requires_access_level(1)
def admin_edit_user(user_type):
    cur = mysql.connection.cursor()
    cur.execute(f"SELECT {user_type}_ID, Name, Address, Age, Gender, Personal_Contact FROM {user_type}")
    users = cur.fetchall()
    cur.close()

    form_1 = AddUser()
    if form_1.validate_on_submit():
        print("Form validated")
        cur = mysql.connection.cursor()
        # print(form_1.users.data, form_1.username.data)
        user = identify_class(user_type).get_by_username(form_1.username.data)
        if user:
            flash('Username already exists.', category='danger')
            return render_template('admin_add_del_user.html', user_type=user_type, user_type_list=users, form=form_1,  user=current_user)
        cur.execute(f"INSERT INTO {user_type} (Username, Password, Name, Address, Age, Gender, Personal_Contact) VALUES ('{form_1.username.data}', '{generate_password_hash(form_1.password1.data, method='sha256')}', '{form_1.name.data}', '{form_1.address.data}', '{form_1.age.data}', '{form_1.gender.data}', '{form_1.contact_number.data}')")
        mysql.connection.commit()
        cur.close()
        flash(f'Successfully added user {form_1.name.data}', 'success')
        return redirect(url_for('adm.admin_edit_user', user_type=user_type, user=current_user))

    return render_template('admin_add_del_user.html', user_type=user_type, user_type_list=users, form=form_1,  user=current_user) 

@adm.route('/admin/delete/<user_type>/<user_id>', methods=['GET', 'POST'])
@adm.route('/admin/delete/<user_type>/<user_id>/', methods=['GET', 'POST'])
@login_required
@requires_access_level(1)
def admin_delete_user(user_type, user_id):
    cur = mysql.connection.cursor()
    if user_type == 'Doctor':
        cur.execute(f"DELETE FROM Drugs_Prescribed WHERE Treatment_ID IN (SELECT Treatment_ID FROM Treatment WHERE {user_type}_ID = {user_id})")
        mysql.connection.commit()
        cur.execute(f"DELETE FROM Treatment WHERE {user_type}_ID = {user_id}")
        mysql.connection.commit()
        cur.execute(f"DELETE FROM Appointment WHERE {user_type}_ID = {user_id}")
        mysql.connection.commit()
    if user_type == 'Administrator':
        cur.execute(f"SELECT * FROM Administrator")
        if current_user.Administrator_ID == int(user_id):
            flash(f'Cannot delete current administrator', 'danger')
            return redirect(url_for('admin.admin_edit_user', user_type=user_type, user=current_user))
    cur.execute(f"DELETE FROM {user_type} WHERE {user_type}_ID = '{user_id}'")
    mysql.connection.commit()
    cur.close()
    flash(f'Successfully deleted {user_type} with ID {user_id}', 'success')
    return redirect(url_for('adm.admin_edit_user', user_type=user_type, user=current_user))

@adm.route('/admin/add_room', methods=['GET', 'POST'])
@adm.route('/admin/add_room/', methods=['GET', 'POST'])
@login_required
@requires_access_level(1)
def admin_add_room():
    form = AddRoom()
    if form.validate_on_submit():
        print("Form validated")
        cur = mysql.connection.cursor()
        cur.execute(f"INSERT INTO Room (Room_Num, Floor) VALUES ({form.num.data}, {form.floor.data})")
        mysql.connection.commit()
        cur.close()
        flash(f'Successfully added room {form.num.data}', 'success')
        return redirect(url_for('adm.admin_add_room'))
    # else:
    #     flash(f'Error adding user {form.name.data}', 'danger')

    return render_template('admin_add_room.html', form=form,  user=current_user)