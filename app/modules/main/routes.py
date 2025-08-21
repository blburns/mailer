"""
Main Application Routes
"""

from flask import render_template
from app.main import bp


@bp.route('/')
def index():
    """Homepage."""
    return render_template('main/index.html', title='Home')


@bp.route('/about')
def about():
    """About page."""
    return render_template('main/about.html', title='About')


@bp.route('/status')
def status():
    """System status page."""
    return render_template('main/status.html', title='System Status')
