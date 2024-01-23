from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['JWT_SECRET_KEY'] = 'secret-key'

CORS(app)
db = SQLAlchemy(app)
jwt = JWTManager(app)

#Define database models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())

    def __init__(self, title, content, author):
        self.title = title
        self.content = content
        self.author = author

# Routes
@app.route('/api/user/register', methods=['POST'])
def register():
    username = request.json.get('username')
    password = request.json.get('password')
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        error_message = 'Username already registered.'
        return jsonify({'error': error_message}), 400
    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created successfully!'}), 201

@app.route('/api/user/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    user = User.query.filter_by(username=username).first()
    if not user or password != user.password:
        return jsonify({'message': 'Invalid username or password'}), 401
    access_token = create_access_token(identity=user.id)
    return jsonify({'access_token': access_token}), 200

@app.route('/api/posts', methods=['GET'])
@jwt_required()
def get_posts():
    posts = BlogPost.query.all()
    results = []
    for post in posts:
        results.append({'id':post.id, 'title':post.title, 'content':post.content, 'author':post.author, 'timestamp':post.timestamp})
    return jsonify(results), 200

@app.route('/api/posts', methods=['POST'])
@jwt_required()
def create_post():
    title = request.json.get('title')
    content = request.json.get('content')
    author = request.json.get('author')
    current_user = get_jwt_identity()
    new_post = BlogPost(title=title, content=content, author=author)
    db.session.add(new_post)
    db.session.commit()
    return jsonify({'message':'Post created successfully!'}), 201

  @app.route('/api/posts/<int:post_id>', methods=['GET'])
@jwt_required()
def get_post(post_id):
    post = BlogPost.query.get(post_id)
    if not post:
        return jsonify({'message':'Post not found'}), 400
    result = {'id':post.id, 'title':post.title, 'content':post.content, 'author':post.author, 'timestamp':post.timestamp}
    return jsonify(result), 200

@app.route('/api/posts/<int:post_id>', methods=['PUT'])
@jwt_required()
def update_post(post_id):
    post = BlogPost.query.get(post_id)
    if not post:
        return jsonify({'message':'Post not found'}), 404
    post.title = request.json.get('title', post.title)
    post.content = request.json.get('content', post.content)
    db.session.commit()
    return jsonify({'message':'Post updated successfully!'}), 200

@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
@jwt_required()
def delete_post(post_id):
    post = BlogPost.query.get(post_id)
    if not post:
        return jsonify({'message':'Post not found'}), 404
    db.session.delete(post)
    db.session.commit()
    return jsonify({'message':'Post deleted successfully!'}), 200

if __name__ == '__main__':
    #db.create_all()
    app.run(debug=True)
