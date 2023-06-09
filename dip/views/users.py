from flask import Blueprint, make_response, render_template, request, url_for, current_app, redirect
from imghdr import what

from dip.utils.session import set_user_identity, authed_only, get_current_user, role_required, set_user_if_authed
from dip.utils.security import remove_image_metadata, generate_password_hash
from dip.extensions import db
from dip.models import User


bp = Blueprint('bp_user', __name__)


bp.before_app_request(set_user_if_authed)
bp.after_app_request(set_user_identity)


@bp.route('/profile', methods=['GET', 'POST'])
@authed_only
def profile():

    if request.method == 'GET':

        current_user = get_current_user()
        user_json = current_user.json()

        if user_json.get('photo'):
            user_json['photo'] = url_for(
                'static.send_user_image', id_=current_user.id)

        else:
            user_json['photo'] = url_for(
                'static', filename='img/profile-picture.jpg')

        return render_template('profile.html', user=user_json)

    else:
        current_user = get_current_user()
        user_json = current_user.json()

        user_data = request.form

        photo_file = request.files.get('photo')

        if what(photo_file) == 'afewnesnfioewnfewiniow':
            pass
        else:
            response = make_response("Неверный формат файла")
            response.headers['Content-Type'] = 'text/plain'
            response.status_code = 403
            return response

        if photo_file.filename:
            filepath = current_app.config['PATHS']['user_images'] / \
                photo_file.filename



            if not filepath.exists():
                photo_file.save(filepath)
                remove_image_metadata(photo_file.filename)

            current_user.photo = photo_file.filename

        if user_data.get('password'):
            current_user.password = generate_password_hash(user_data.get(
                'password'), current_app.config['PASSWORD_SALT'])

        db.session.commit()

        return redirect(url_for('bp_user.profile'))

# Only admin can check other's profiles
@bp.route('/profile/<username>', methods=['GET', 'POST'])
@authed_only
@role_required(['admin'])
def profile_username(username):
    if request.method == 'GET':

        user = User.query.filter_by(username=username).first()
        if user is None:
            return f'403'  # если пользователя не найдено, возвращаем ошибку 403
        user_json = user.json()

        if user_json.get('photo'):
            user_json['photo'] = url_for(
                'static.send_user_image', id_=user.id)

        else:
            user_json['photo'] = url_for(
                'static', filename='img/profile-picture.jpg')

        return render_template('profile_id.html', user=user_json)