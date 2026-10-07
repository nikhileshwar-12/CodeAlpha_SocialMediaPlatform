# CodeAlpha Social Media Platform

A full-stack social media web application built with **Django**. Users can
register, build a profile, follow other users, and share posts through a
personalised feed and an explore page.

![Django](https://img.shields.io/badge/Django-092E20?style=flat-square&logo=django&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white)

---

## Features

### Accounts
- User registration, login and logout
- Profile pages with avatars and bio text
- Profile editing for the logged-in user
- Follow / unfollow other users
- Follower and following lists
- User search
- Automatic profile creation on signup (Django signals)

### Posts
- Personalised feed showing posts from people you follow
- Explore page for discovering new posts
- Individual post detail pages
- Reusable post-card and timeline templates
- Post creation from the UI

### Tooling
- `seed_data` management command that populates demo users and posts
- Custom responsive CSS and vanilla JavaScript — no heavy frontend framework
- Custom Django admin configuration for both apps

---

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Python, Django |
| Database | SQLite (development) |
| Frontend | Django templates, vanilla CSS and JavaScript |
| Auth | Django's built-in authentication system |

---

## Getting started

### 1. Clone the repository

    git clone https://github.com/nikhileshwar-12/CodeAlpha_SocialMediaPlatform.git
    cd CodeAlpha_SocialMediaPlatform

### 2. Create and activate a virtual environment

    # Windows
    python -m venv venv
    venv\Scripts\activate

    # macOS / Linux
    python3 -m venv venv
    source venv/bin/activate

### 3. Install dependencies

    pip install -r requirements.txt

### 4. Set up the database

    python manage.py migrate

### 5. (Optional) Load demo content

    python manage.py seed_data

### 6. Create an admin account

    python manage.py createsuperuser

### 7. Run the development server

    python manage.py runserver

Open http://127.0.0.1:8000/ to use the app, or http://127.0.0.1:8000/admin/ to manage content.

---

## Project structure

    CodeAlpha_SocialMediaPlatform/
    ├── manage.py
    ├── requirements.txt
    ├── socialmedia/                # Project configuration
    │   ├── settings.py
    │   ├── urls.py
    │   ├── asgi.py
    │   └── wsgi.py
    ├── accounts/                   # User accounts app
    │   ├── models.py               # Profile and follow relationships
    │   ├── views.py                # Register, login, profile, follow, search
    │   ├── forms.py                # Signup, login and profile forms
    │   ├── signals.py              # Auto-create profile on signup
    │   └── management/commands/seed_data.py
    ├── posts/                      # Posts app
    │   ├── models.py
    │   ├── views.py                # Feed, explore and post detail views
    │   ├── forms.py
    │   └── utils.py
    ├── templates/
    │   ├── base.html
    │   ├── accounts/               # login, register, profile, search, follow lists
    │   └── posts/                  # feed, explore, post detail, post cards
    └── static/
        ├── css/style.css
        └── js/main.js

---

## Notes

- Built as a CodeAlpha Web Development internship task.
- `SECRET_KEY` and `DEBUG = True` in `settings.py` are for local development only.
  A production deployment would load these from environment variables and set `DEBUG = False`.
- The SQLite database is git-ignored, so run `migrate` and `seed_data` after cloning.

## License

MIT
