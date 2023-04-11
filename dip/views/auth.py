from flask import Blueprint, make_response, render_template, request, url_for, current_app, redirect, g
from sqlalchemy import text

from dip.utils.session import get_current_user, create_session
from dip.utils.session import set_user_identity, SESSION_COOKIE_NAME
from dip.utils.security import generate_password_hash
from dip.models import User
from dip.extensions import db


bp = Blueprint('bp_auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':

        user = get_current_user()

        if not user:
            return render_template('login.html')

        return redirect(url_for('bp_user.profile'))

    if request.method == 'POST':
        username = request.form['username']
        plain_password = request.form['password']
        # SQL injection prevention in login page
        if ("'" or '"' or "-" or '*' or '#' or '`' or '~' or '&') in username:
            return render_template('login.html', error='Штопанный задрот, на сервере запрещено использование SQL инъекций'), 403
        hashed_password = generate_password_hash(plain_password, current_app.config['PASSWORD_SALT'])
        
        user_query = db.session.query(User).filter(text(f"username='{username}' AND password='{hashed_password}'"))

        conn = db.engine.raw_connection()
        cur = conn.cursor()
        user = cur.execute(str(user_query)).fetchone()
        
        # 500 error if user is None fix.
        if user is None:
            return render_template('login.html', error='Неверный логин или пароль'), 403
        user = dict(zip([
            'id',
            'first_name',
            'second_name',
            'patronymic',
            'username',
            'photo',
            'email',
            'password',
            'phone_number',
            'job_title',
            'role',
        ], user))

        session = create_session(user['username'], user['role'])
        
        # Cookie TTL limitation
        resp = redirect(url_for('bp_user.profile'))
        resp.set_cookie(SESSION_COOKIE_NAME, session, max_age=300)

        g.user = user

        return resp


@bp.route('/logout', methods=['GET'])
def logout():
    resp = make_response(redirect(url_for('bp_auth.login')))
    resp.delete_cookie(SESSION_COOKIE_NAME)
    return resp