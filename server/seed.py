#!/usr/bin/env python3

from random import randint, choice as rc

from faker import Faker

from app import app
from models import db, Article, User

fake = Faker()

with app.app_context():

    print("Deleting all records...")
    Article.query.delete()
    User.query.delete()

    print("Creating users...")
    users = []
    usernames = []

    # ✅ Ensure at least one guaranteed user for the test
    user = User(username='testuser')
    users.append(user)

    # Create additional random users
    for i in range(24):
        username = fake.first_name()
        while username in usernames or username == 'testuser':
            username = fake.first_name()

        usernames.append(username)

        user = User(username=username)
        users.append(user)

    db.session.add_all(users)

    print("Creating articles...")
    articles = []
    for i in range(100):
        content = fake.paragraph(nb_sentences=8)
        preview = content[:25] + '...'

        article = Article(
            author=fake.name(),
            title=fake.sentence(),
            content=content,
            preview=preview,
            minutes_to_read=randint(1, 20),
            is_member_only=rc([True, False, False])  # Mostly public, some member-only
        )

        articles.append(article)

    db.session.add_all(articles)

    db.session.commit()
    print("Seeding complete.")
