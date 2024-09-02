from flask import Flask, request, jsonify, session
import bcrypt
from helper import execute_query, handle_errors, protected_route
from dotenv import load_dotenv
import os

load_dotenv("variables.env")
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET')
app.config['SESSION_COOKIE_HTTPONLY'] = True



@app.route('/register', methods=['POST'])
@handle_errors
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({
            'message': 'Field is empty'
        }), 400

    hash_password = bcrypt.hashpw(
        password.encode('utf-8'),
        bcrypt.gensalt()
    )

    query = 'INSERT INTO users(username, email, password_hash) VALUE (%s, %s, %s)'
    result = execute_query(query, (username, email, hash_password), commit=True)

    if result is None:
        return jsonify({
            'message': 'Registration Error'
        }), 500
    
    return jsonify({
        'message': 'Registered successfully'
    }), 201




@app.route('/login', methods=['POST'])
@handle_errors
def login():
    data = request.get_json()
    email_or_username = data.get('email_or_username')
    password = data.get('password')

    if not email_or_username or not password:
        return jsonify({
            'message': 'Field is empty'
        }), 400
    
    query = 'SELECT user_id, username, password_hash FROM users WHERE username = %s OR email = %s'
    user = execute_query(query, (email_or_username, email_or_username), fetch_one=True)
        
    if user and bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
        session['user_info'] = (user[0], user[1])

        return jsonify({
            'message': 'Login successfully',
            'user_id':  session['user_info'][0]
        }), 200
    
    else:
        return jsonify({
            'message': 'Invalid credential'
        }), 400



@app.route('/post', methods=['POST'])
@handle_errors
@protected_route
def create_post():
    data = request.get_json()
    content = data.get('content')
    user_id = session['user_info'][0]

    if not content:
        return jsonify({
            'message': 'Content is required'
        }), 400
    
    query = 'INSERT INTO posts(user_id, content) VALUES (%s, %s)'
    result = execute_query(query, (user_id, content), commit=True)

    if result is None:
        return jsonify({
            'message': 'Error in creating post'
        }), 500
    
    return jsonify({
        'message': 'Post created successfully!'
    }), 201



@app.route('/post/<int:post_id>', methods=['PUT'])
@handle_errors
@protected_route
def update_post(post_id):
    data = request.get_json()
    content = data.get('content')
    user_id = session['user_info'][0]

    if not content:
        return jsonify({
            'message': 'Content is required'
        }), 400
    
    query = 'UPDATE posts SET content = %s WHERE post_id = %s AND user_id = %s'
    result = execute_query(query, (content, post_id, user_id), commit=True)
    print(result)

    if result is None:
        return jsonify({
            'message': 'Error in updating post'
        }), 500
    
    return jsonify({
        'message': 'Post updated successfully'
    }), 201



@app.route('/post/<int:post_id>', methods=['GET'])
@handle_errors
@protected_route
def view_post(post_id):
    user_id = session['user_info'][0]
    query = 'SELECT post_id, content, created_at, updated_at FROM posts where post_id = %s AND user_id = %s'
    post = execute_query(query, (post_id, user_id), fetch_one=True)

    if post is None:
        return jsonify({
            'message': 'Error in view user posts'
        }), 500
    
    return jsonify({
        'message': 'View Post',
        'posts': post
    }), 200



@app.route('/post/<int:post_id>', methods=['DELETE'])
@handle_errors
@protected_route
def delete_post(post_id):
    user_id = session['user_info'][0]
    query = 'DELETE FROM posts WHERE post_id = %s AND user_id = %s'
    result = execute_query(query, (post_id, user_id), commit=True)

    if result is None:
        return jsonify({
            'message': 'Error in deleting post'
        }), 500
    
    return jsonify({
        'message': 'Post deleted successfully'
    }), 201



@app.route('/post/view', methods=['GET'])
@handle_errors
@protected_route
def view_user_posts():
    user_id = session['user_info'][0]
    query = 'SELECT post_id, content, created_at, updated_at FROM posts where user_id = %s ORDER By created_at DESC'
    posts = execute_query(query, (user_id,))

    if posts is None:
        return jsonify({
            'message': 'Error in view user posts'
        }), 500
    
    return jsonify({
        'message': 'View All User Posts',
        'posts': posts
    }), 200



@app.route('/posts', methods=['GET'])
@handle_errors
@protected_route
def view_posts():
    print(session['user_info'])
    query =  """
        SELECT post_id, content, posts.created_at, users.username,
            (SELECT COUNT(*) FROM likes WHERE likes.post_id = posts.post_id) AS like_count
        FROM posts
        JOIN users on users.user_id = posts.user_id
        ORDER BY created_at DESC
    """
    posts = execute_query(query)
    if posts is None:
        return jsonify({
            'message': 'Error in view posts'
        }), 500
    
    return jsonify({
        'message': 'View All Posts',
        'posts': posts
    }), 200



@app.route('/posts/<int:post_id>/like', methods=['POST'])
@handle_errors
@protected_route
def like_post(post_id):
    user_id = session['user_info'][0]
    query = "INSERT INTO likes (user_id, post_id) VALUES (%s, %s)"
    result = execute_query(query, (user_id, post_id), commit=True)
    
    if result is None:
        return jsonify({
            'message': 'Post already liked or error in liking post'
        }), 500
    
    return jsonify({
        'message': 'Post liked successfully'
    }), 201



@app.route('/posts/<int:post_id>/unlike', methods=['DELETE'])
@handle_errors
@protected_route
def unlike_post(post_id):
    user_id = session['user_info'][0]
    query = "DELETE FROM likes WHERE user_id = %s AND post_id = %s"
    result = execute_query(query, (user_id, post_id), commit=True)
    
    if result is None:
        return jsonify({
            'message': 'Error unliking post'
        }), 500
    
    return jsonify({
        'message': 'Post unliked successfully'
    }), 200



@app.route('/posts/<int:post_id>/countlikes', methods=['GET'])
@handle_errors
@protected_route
def count_likes_post(post_id):
    query = 'SELECT COUNT(*) FROM likes WHERE post_id = %s'
    result = execute_query(query, (post_id,), fetch_one=True)
    
    if result is None:
        return jsonify({
            'message': 'Error counting likes'
        }), 500
    
    return jsonify({
        'message': 'likes count',
        'count': result
    }), 200



@app.route('/logout', methods=['POST'])
@handle_errors
@protected_route
def logout():
    session.pop('user_info', None)
    return jsonify({
        'message': 'Logout successfully'
    }), 200



if __name__ == '__main__':
   app.run(debug=True)




