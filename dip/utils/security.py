import os
import hmac
import hashlib
import pathlib
import subprocess

from flask import current_app


ALLOWED_IMAGE_EXTENSIONS = set(['png', 'jpg', 'jpeg'])


def generate_password_hash(password, salt):
    # md5 to sha256
    return hashlib.sha256((password + salt).encode('utf-8')).hexdigest()


def is_correct_password(plain_password, hashed_password, salt):

    return generate_password_hash(plain_password, salt) == hashed_password


def is_valid_signature(identity, secret_key):

    username = identity.get('username', '')
    role = identity.get('role', '')

    signature = identity.get('signature', '')

    return hmac.compare_digest(
        signature,
        create_signature(username, role, secret_key)
    )


def create_signature(username, role, secret_key):
    msg = username + role

    signature = hmac.new(
        secret_key.encode('utf-8'),
        msg.encode('utf-8'), hashlib.sha256
    ).hexdigest()

    return signature

# Замена os.system на subprocess
def remove_image_metadata(filename):
    filepath = pathlib.Path(current_app.root_path).parent / current_app.config["PATHS"]["user_images"] / filename
    command = ['exiftool', '-EXIF=', str(filepath)]
    subprocess.run(command)


