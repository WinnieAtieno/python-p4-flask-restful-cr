#!/usr/bin/env python3
from datetime import datetime
from flask import Flask, request, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Newsletter

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///newsletters.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

db.init_app(app)
migrate = Migrate(app, db)

api = Api(app)

class Home(Resource):
    def get(self):
        response = make_response({"message": "Welcome to the RESTful API"}, 200)
        return response

class Newsletters(Resource):
    def get(self):
        newsletters = [newsletter.to_dict() for newsletter in Newsletter.query.all()]
        response = make_response(newsletters, 200)
        return response

    def post(self):
        data = request.get_json()
        
        title = data.get('title')
        body = data.get('body')
        published_at = data.get('published_at')
        edited_at = data.get('edited_at')

        if not title or not body:
            return make_response({'message': 'Title and body are required.'}, 400)

        try:
            if published_at:
                published_at = datetime.strptime(published_at, "%Y-%m-%d %H:%M:%S")
            else:
                published_at = datetime.now()

            new_newsletter = Newsletter(
                title=title,
                body=body,
                published_at=published_at,
                edited_at=edited_at
            )

          
            db.session.add(new_newsletter)
            db.session.commit()

            response = make_response(new_newsletter.to_dict(), 201)
        except ValueError:
            return make_response({'message': 'Invalid date format. Use YYYY-MM-DD HH:MM:SS.'}, 400)
        except Exception as e:
            db.session.rollback()
            return make_response({'message': str(e)}, 500)

        return response

class NewsletterByID(Resource):
    def get(self, id):
        newsletter = Newsletter.query.filter_by(id=id).first()
        if newsletter:
            response = make_response(newsletter.to_dict(), 200)
            return response
        else:
            response = make_response({"msg": f"Newsletter with ID {id} not found"}, 404)
            return response

api.add_resource(Newsletters, '/newsletters')
api.add_resource(NewsletterByID, '/newsletters/<int:id>')  
api.add_resource(Home, '/')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
