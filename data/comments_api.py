import flask

from . import db_session
from .comments import Comment
from flask import jsonify, request

blueprint = flask.Blueprint('news_api', __name__, template_folder='templates')


@blueprint.route('/api/comment')
def get_news():
    db_sess = db_session.create_session()
    comments = db_sess.query(Comment).all()
    return jsonify({
        'comments': [item.to_dict(only=('title', 'content', 'user.name')) for item in comments]
    })


@blueprint.route('/api/comment/<int:comment_id>', methods=['GET', 'POST'])
def get_one_news(comment_id):
    db_sess = db_session.create_session()
    comment = db_sess.query(Comment).get(comment_id)
    if not comment:
        return jsonify({'error': 'Not found'})
    return jsonify({
        'news': comment.to_dict(only=('title', 'content', 'user.name', 'is_private'))
    })


@blueprint.route('/api/comment', methods=['POST'])
def add_news():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all([key in request.json for key in ['title', 'content', 'user_id', 'is_private']]):
        return jsonify({'error': 'Bad request'})
    db_sess = db_session.create_session()
    comment = Comment(
        title=request.json['title'],
        content=request.json['content'],
        user_id=request.json['user_id'],
    )
    db_sess.add(comment)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/comment/<int:comment_id>', methods=['DELETE'])
def delete_news(comment_id):
    db_sess = db_session.create_session()
    comment = db_sess.query(Comment).get(comment_id)
    if not comment:
        return jsonify({'error': 'Not found'})
    db_sess.delete(comment)
    db_sess.commit()
    return jsonify({'success': 'OK'})