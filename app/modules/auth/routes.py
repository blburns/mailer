"""
Authentication Routes
"""

from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.urls import url_parse
from app.modules.auth import bp
from app.modules.auth.forms import LoginForm, ChangePasswordForm
from app.models import User, AuditLog
from app.extensions import db, bcrypt
from datetime import datetime


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember_me.data)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # Log the login
            audit_log = AuditLog(
                user_id=user.id,
                action='login',
                resource_type='user',
                resource_id=str(user.id),
                ip_address=request.remote_addr
            )
            db.session.add(audit_log)
            db.session.commit()
            
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('dashboard.index')
            return redirect(next_page)
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('auth/login.html', title='Sign In', form=form)


@bp.route('/logout')
@login_required
def logout():
    # Log the logout
    audit_log = AuditLog(
        user_id=current_user.id,
        action='logout',
        resource_type='user',
        resource_id=str(current_user.id),
        ip_address=request.remote_addr
    )
    db.session.add(audit_log)
    db.session.commit()
    
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if bcrypt.check_password_hash(current_user.password_hash, form.current_password.data):
            current_user.password_hash = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
            db.session.commit()
            
            # Log the password change
            audit_log = AuditLog(
                user_id=current_user.id,
                action='change_password',
                resource_type='user',
                resource_id=str(current_user.id),
                ip_address=request.remote_addr
            )
            db.session.add(audit_log)
            db.session.commit()
            
            flash('Your password has been changed.', 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash('Invalid current password.', 'error')
    
    return render_template('auth/change_password.html', title='Change Password', form=form)
