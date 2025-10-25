from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from zooventory.auth import login_required
from zooventory.db import get_db

bp = Blueprint('calculator', __name__, url_prefix='/calculator')

@bp.route('/', methods=['GET', 'POST'])
@login_required
def feed_animal():
    db = get_db()

    if request.method == 'POST':
        animal_id = request.form['animal_id']
        food_id = request.form['food_id']
        amount = request.form['amount']

        if not animal_id or not food_id or not amount:
            flash('Please fill out all fields.')
            return redirect(url_for('calculator.feed_animal'))

        try:
            amount = float(amount)
        except ValueError:
            flash('Amount must be a number.')
            return redirect(url_for('calculator.feed_animal'))

        food = db.execute(
            'SELECT * FROM food WHERE id = ? AND owner_id = ?',
            (food_id, g.user['id'])
        ).fetchone()

        if food is None:
            flash('Invalid food selection.')
            return redirect(url_for('calculator.feed_animal'))

        if food['amount'] < amount:
            flash(f'Not enough {food['name']} left! You only have {food['amount']}.')
            return redirect(url_for('calculator.feed_animal'))

        db.execute(
            'UPDATE animal SET last_fed = ? WHERE id = ? AND owner_id = ?',
            (amount, animal_id, g.user['id'])
        )

        db.execute(
            'UPDATE food SET amount = amount - ? WHERE id = ? AND owner_id = ?',
            (amount, food_id, g.user['id'])
        )

        db.commit()
        flash('Feeding recorded successfully!')
        return redirect(url_for('calculator.feed_animal'))

    animals = get_db().execute(
        'SELECT id, name, species FROM animal WHERE owner_id = ?',
        (g.user['id'],)
    ).fetchall()

    food = get_db().execute(
        'SELECT id, name, amount, measurement FROM animal WHERE owner_id = ?',
        (g.user['id'],)
    ).fetchall()

    return render_template('calculator/feed.html', animals=animals, food=food)