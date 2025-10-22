from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from zooventory.auth import login_required
from zooventory.db import get_db

bp = Blueprint('food', __name__, url_prefix='/food')

@bp.route('/index')
@login_required
def index():
    db = get_db()
    food = db.execute(
        'SELECT f.id, name, amount, measurement, owner_id'
        ' FROM food f JOIN user u ON f.owner_id = u.id'
        ' ORDER BY name '
    ).fetchall()
    return render_template('food/index.html', food=food)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        name = request.form['name']
        amount = request.form['amount']
        measurement = request.form['measurement']
        error = None

        if not name:
            error = 'Name is required.'
        elif not amount:
            error = 'Amount is required.'
        elif not measurement:
            error = 'Measurement is required.'

        if error is not None:
            flash(error)

        else:
            db = get_db()
            db.execute(
                'INSERT INTO food (name, amount, measurement, owner_id)'
                'VALUES (?, ?, ?, ?)',
                (name, amount, measurement, g.user['id'])
            )
            db.commit()
            return redirect(url_for('food.index'))

    return render_template('food/create.html')

def get_food(id, check_owner=True):
    food = get_db().execute(
        'SELECT f.id, name, amount, measurement, owner_id'
        ' FROM food f JOIN user u ON f.owner_id = u.id'
        ' WHERE f.id = ?',
        (id,)
    ).fetchone()

    if food is None:
        abort(404, f" Food id {id} doesn't exist.")

    if check_owner and food['owner_id'] != g.user['id']:
        abort(403)

    return food

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    food = get_food(id)

    if request.method == 'POST':
        name = request.form['name']
        amount = request.form['amount']
        measurement = request.form['measurement']
        error = None

        if not name:
            error = 'Name is required.'
        elif not amount:
            error = 'Amount is required.'
        elif not measurement:
            error = 'Measurement is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE food SET name = ?, amount = ?, measurement = ?'
                ' WHERE id = ?',
                (name, amount, measurement, id)
            )
            db.commit()
            return redirect(url_for('food.index'))

    return render_template('food/update.html', food=food)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_food(id)
    db = get_db()
    db.execute('DELETE FROM food WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('food.index'))