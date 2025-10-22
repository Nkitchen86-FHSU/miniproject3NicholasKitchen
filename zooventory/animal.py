from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from zooventory.auth import login_required
from zooventory.db import get_db

bp = Blueprint('animal', __name__, url_prefix='/animal')

@bp.route('/index')
@login_required
def index():
    db = get_db()
    animals = db.execute(
        'SELECT a.id, name, species, age, last_fed, owner_id'
        ' FROM animal a JOIN user u ON a.owner_id = u.id'
        ' ORDER BY last_fed DESC '
    ).fetchall()
    return render_template('animal/index.html', animals=animals)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        name = request.form['name']
        species = request.form['species']
        age = request.form['age']
        error = None

        if not name:
            error = 'Name is required.'
        elif not species:
            error = 'Species is required.'
        elif not age:
            error = 'Age is required.'

        if error is not None:
            flash(error)

        else:
            db = get_db()
            db.execute(
                'INSERT INTO animal (name, species, age, owner_id)'
                'VALUES (?, ?, ?, ?)',
                (name, species, age, g.user['id'])
            )
            db.commit()
            return redirect(url_for('animal.index'))

    return render_template('animal/create.html')

def get_animal(id, check_owner=True):
    animal = get_db().execute(
        'SELECT a.id, name, species, age, last_fed, owner_id'
        ' FROM animal a JOIN user u ON a.owner_id = u.id'
        ' WHERE id = ?',
        (id,)
    ).fetchone()

    if animal is None:
        abort(404, f" Animal id {id} doesn't exist.")

    if check_owner and animal['owner_id'] != g.user['id']:
        abort(403)

    return animal

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    animal = get_animal(id)

    if request.method == 'POST':
        name = request.form['name']
        species = request.form['species']
        age = request.form['age']
        error = None

        if not name:
            error = 'Name is required.'
        elif not species:
            error = 'Species is required.'
        elif not age:
            error = 'Age is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE animal SET name = ?, species = ?, age = ?'
                ' WHERE id = ?',
                (name, species, age, id)
            )
            db.commit()
            return redirect(url_for('animal.index'))

    return render_template('animal/update.html', animal=animal)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_animal(id)
    db = get_db()
    db.execute('DELETE FROM animal WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('animal.index'))