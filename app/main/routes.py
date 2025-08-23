"""
Main Application Routes
"""

from flask import render_template
from flask_login import login_required
from app.main import bp


@bp.route('/')
@login_required
def index():
    """Homepage."""
    # return redirect(url_for('dashboard.index'))
    return render_template('modules/main/index.html', title='Home')


@bp.route('/about')
@login_required
def about():
    """About page."""
    return render_template('modules/main/about.html', title='About')


@bp.route('/status')
@login_required
def status():
    """System status page."""
    return render_template('modules/main/status.html', title='System Status')
