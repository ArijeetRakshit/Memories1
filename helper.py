from flask import jsonify, session
from db import create_db_connection
from functools import wraps

def execute_query(query, args=(), fetch_one=False, commit=False):
    try:
        ctx = create_db_connection()
        if ctx:
            cursor = ctx.cursor()
            cursor.execute(query, args)

            if commit:
                ctx.commit()

            if fetch_one:
                res = cursor.fetchone()
            else: 
                res = cursor.fetchall()

            cursor.close()
            ctx.close()
            return res
        
    except Exception as e:
         raise e

    
def handle_errors(callback):
    @wraps(callback)

    def decorated_func(*args, **kwargs):
        try:
            return callback(*args, **kwargs)
        
        except Exception as e:
            return jsonify({
                'error': str(e)
            }), 500
        
    return decorated_func


def protected_route(callback):
    @wraps(callback)

    def decorated_func(*args, **kwargs):
        try:
            if session and session['user_info']:
                return callback(*args, **kwargs)
            return jsonify({
                    'message': 'Cannot access, Unauthorised'
                }), 401
        except Exception:
            raise Exception('Some error occured')
    
    return decorated_func
