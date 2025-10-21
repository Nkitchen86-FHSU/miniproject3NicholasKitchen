from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from zooventory.auth import login_required
from zooventory.db import get_db

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@bp.route('/dashboard')
def dashboard():
    return render_template('dashboard/dashboard.html')