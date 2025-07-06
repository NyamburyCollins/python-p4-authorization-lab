import flask
import pytest

from app import app
from models import db, Article, User

app.secret_key = b'a\xdb\xd2\x13\x93\xc1\xe9\x97\xef2\xe3\x004U\xd1Z'

@pytest.fixture(autouse=True)
def setup_database():
    with app.app_context():
        db.session.query(User).delete()
        db.session.query(Article).delete()

        # Seed user
        user = User(username='testuser')
        db.session.add(user)

        # Seed member-only articles
        articles = [
            Article(title='Test Article 1', content='Content 1', preview='Preview 1', minutes_to_read=5, is_member_only=True, author='Author 1'),
            Article(title='Test Article 2', content='Content 2', preview='Preview 2', minutes_to_read=3, is_member_only=True, author='Author 2')
        ]
        db.session.add_all(articles)
        db.session.commit()

class TestApp:
    '''Flask API in app.py'''

    def test_can_only_access_member_only_while_logged_in(self):
        '''allows logged in users to access member-only article index at /members_only_articles.'''
        with app.test_client() as client:
            client.get('/clear')

            user = User.query.filter_by(username='testuser').first()
            client.post('/login', json={'username': user.username})

            response = client.get('/members_only_articles')
            assert response.status_code == 200

            client.delete('/logout')

            response = client.get('/members_only_articles')
            assert response.status_code == 401

    def test_member_only_articles_shows_member_only_articles(self):
        '''only shows member-only articles at /members_only_articles.'''
        with app.test_client() as client:
            client.get('/clear')

            user = User.query.filter_by(username='testuser').first()
            client.post('/login', json={'username': user.username})

            response_json = client.get('/members_only_articles').get_json()
            for article in response_json:
                assert article['is_member_only'] == True

    def test_can_only_access_member_only_article_while_logged_in(self):
        '''allows logged in users to access full member-only articles at /members_only_articles/<int:id>.'''
        with app.test_client() as client:
            client.get('/clear')

            user = User.query.filter_by(username='testuser').first()
            client.post('/login', json={'username': user.username})

            article = Article.query.filter_by(is_member_only=True).first()

            response = client.get(f'/members_only_articles/{article.id}')
            assert response.status_code == 200

            client.delete('/logout')

            response = client.get(f'/members_only_articles/{article.id}')
            assert response.status_code == 401
