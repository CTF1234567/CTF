from flask import Blueprint, make_response, render_template, request, url_for, current_app, redirect, render_template_string
from sqlalchemy import desc
from slugify import slugify
from flask import flash
from dip.utils.session import authed_only, get_current_user
from dip.extensions import db
from dip.models import WikiPage

import html

bp = Blueprint('bp_wiki', __name__)


@bp.route('/wiki', methods=['GET', 'POST'])
@authed_only
def wiki():

    wiki_pages = WikiPage.query.order_by(desc(WikiPage.created_at)).all()

    return render_template('wiki.html', wiki_pages=wiki_pages)


@bp.route('/wiki/<slug>', methods=['GET'])
@authed_only
def wiki_slug(slug):
    wiki_page = WikiPage.query.filter_by(slug=slug).first()

    if not wiki_page:
        return render_template('404.html'), 404
    #SSTI?
    return render_template('wiki_slug.html', wiki_page=wiki_page.json())


@bp.route('/wiki/create', methods=['GET', 'POST'])
@authed_only
def wiki_create():

    if request.method == 'GET':
        return render_template('wiki_create.html')

    wiki_data = request.form

    title = wiki_data.get('title')

    if not title:
        # Error isn't render fix
        flash('Не указан заголовок')
        return render_template('wiki_create.html'), 400

    title_exists = WikiPage.query.filter_by(name=title).first()

    if title_exists:
        # Error isn't render fix
        flash('Запись с таким именем уже существует')
        return render_template('wiki_create.html'), 400

    content = wiki_data.get('content')
    slug = slugify(title)

    current_user = get_current_user()

    wiki_page = WikiPage(
        name=title,
        slug=slug,
        # - content=content
        # + то что ниже
        # Stored XSS fix
        content=html.escape(content),
        owner_id=current_user.id,
    )

    db.session.add(wiki_page)
    db.session.commit()
    
    
    return redirect(url_for('bp_wiki.wiki'))