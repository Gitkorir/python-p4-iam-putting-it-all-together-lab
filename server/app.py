
#!/usr/bin/env python3

from flask import request, session,jsonify
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        data=request.get_json()
        username=data.get('username')
        password=data.get('password')
        image_url=data.get('image_url')
        bio=data.get('bio')
        if not username :
            return {'error':'missing username'},422
        user=User.query.filter(User.username==username).first()
        if user:
            return ({'error':'username already exists'}),422
        new_user=User(username=username,image_url=image_url,bio=bio) 
        new_user.password_hash=password
        db.session.add(new_user)
        db.session.commit()
        session['user_id']=new_user.id
        return ({
                'id':new_user.id,
                'username':new_user.username,
                'image_url':new_user.image_url,
                'bio':new_user.bio
                }),201
    pass

class CheckSession(Resource):
    def get(self):
        user_id=session.get('user_id')
        if user_id:
            user=User.query.filter(User.id==user_id).first()
            if user:
                return {
                    'id':user.id,
                    'username':user.username,
                    'image_url':user.image_url,
                    'bio':user.bio
                },200
        return ({'error':'user not logged in'}),401
    pass

class Login(Resource):
    def post(self):
        data=request.get_json()
        username=data.get('username')
        password=data.get('password')
        user=User.query.filter(User.username==username).first()
        if user and user.authenticate(password):
            session['user_id']=user.id
            return {
                'id':user.id,
                'username':user.username,
                'image_url':user.image_url,
                'bio':user.bio
            },200
        return ({'error':'user not logged in'}),401
    pass

class Logout(Resource):
    def delete(self):
        user_id=session.get('user_id')
        if not user_id:
            return ({'error':'user not logged in'}),401
        else:
            session.pop('user_id')
            return '',204
    pass

class RecipeIndex(Resource):
    def get(self):
        user_id=session.get('user_id')
        if user_id:
            recipes=Recipe.query.filter(Recipe.user_id==user_id).all()
            return [{'title':r.title,'instructions':r.instructions,'minutes_to_complete':r.minutes_to_complete} for r in recipes]
        return ({'error':'user not logged in'}),401
    
    def post(self):
        if 'user_id' in session:
            user_id=session.get('user_id')
            data=request.get_json()
            title=data.get('title')
            instructions=data.get('instructions')
            minutes=data.get('minutes')
            user=User.query.filter(User.id==user_id).first()
            if title and instructions and (50<=len(instructions.strip())):
                new_recipe=Recipe(title=title,instructions=instructions,minutes_to_complete=minutes,user_id=user_id)
                db.session.add(new_recipe)
                db.session.commit()
                return {
                    'title':new_recipe.title,
                    'instructions':new_recipe.instructions,
                    'minutes_to_complete':new_recipe.minutes_to_complete,
                    'user':{               
                        'id':user.id,
                        'username':user.username,
                        'image_url':user.image_url,
                        'bio':user.bio
                      }
                },201
            return ({'error':'invalid recipe'}),422
        return ({'error':'user not logged in'}),401
    pass

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)