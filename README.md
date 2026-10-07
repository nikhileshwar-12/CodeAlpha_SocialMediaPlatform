# 💬 Connectly — Mini Social Media Platform

**CodeAlpha Full Stack Development Internship — Task 2**

A mini social network built with **Django** (Python) on the backend and **HTML, CSS & vanilla JavaScript** on the frontend, using **SQLite** as the database. Users can create profiles, publish posts (text + image), comment, like, follow each other and get a personalised home feed.

---

## ✨ Features

| Area | What's included |
|------|-----------------|
| **User profiles** | Auto-created profile for every user (via Django signals), avatar upload with initials fallback, bio, location, website, join date, post/follower/following counts, edit-profile page |
| **Posts** | Create posts with text (up to 1000 chars) and an optional image, live character counter & image preview, delete own posts |
| **Comments** | Comment on any post, delete your own comments (post owners can moderate comments on their posts) |
| **Like system** | One-click like/unlike with instant AJAX update (heart animation + counter), unique per user/post |
| **Follow system** | Follow/unfollow via AJAX, followers & following lists, "Who to follow" suggestions ranked by popularity, self-follow prevented at DB level |
| **Home feed & Explore** | Home = posts from people you follow + your own; Explore = everyone's posts (public). Both paginated |
| **People search** | Search users by username or name |
| **Authentication** | Register, login, logout; all write actions are login-protected; ownership checks on delete |
| **Admin panel** | Manage users, profiles, posts (with inline comments), comments, likes and follows |
| **Database** | SQLite with models `Profile`, `Follow`, `Post`, `Comment`, `Like` + Django `User` |
| **Responsive UI** | Custom CSS three-column layout that collapses gracefully on tablets and phones |

---

## 🛠️ Tech Stack

- **Backend:** Python 3.10+, Django 5/6
- **Frontend:** HTML5, CSS3, JavaScript (ES6, Fetch API)
- **Database:** SQLite (default Django DB — zero setup)
- **Other:** Pillow (image uploads), Django signals, ORM annotations (`Count`, `Exists`) for an N+1-free feed

---

## 🚀 Getting Started

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/CodeAlpha_SocialMediaPlatform.git
cd CodeAlpha_SocialMediaPlatform

# 2. Create & activate a virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create the database tables
python manage.py migrate

# 5. Load demo users, posts, comments, likes & follows
python manage.py seed_data

# 6. Run the development server
python manage.py runserver
```

Open **http://127.0.0.1:8000/** in your browser.

### Demo accounts (created by `seed_data`)

| Username | Password | Notes |
|----------|----------|-------|
| `aarav`, `diya`, `kabir`, `meera`, `rohan`, `sana` | `demo12345` | Regular users with posts & follows |
| `admin` | `admin123` | Superuser — http://127.0.0.1:8000/admin/ |

---

## 📁 Project Structure

```
CodeAlpha_SocialMediaPlatform/
├── socialmedia/            # Project settings & root URL configuration
├── accounts/               # Users, profiles, follows, auth, search
│   ├── models.py           # Profile, Follow
│   ├── signals.py          # Auto-create Profile on user registration
│   ├── forms.py            # RegisterForm, LoginForm, ProfileForm
│   ├── views.py            # register/login/logout, profile, edit, follow toggle, lists, search
│   ├── urls.py
│   └── management/commands/seed_data.py   # Demo data loader
├── posts/                  # Posts, comments, likes, feed
│   ├── models.py           # Post, Comment, Like
│   ├── utils.py            # annotate_posts() – like/comment counts + liked flag
│   ├── forms.py            # PostForm, CommentForm
│   ├── views.py            # feed, explore, create/delete post, like toggle, comments
│   └── urls.py
├── templates/
│   ├── base.html
│   ├── accounts/           # login, register, profile, profile_edit, follow_list, search, _avatar, _user_card
│   └── posts/              # feed, explore, post_detail, _timeline, _post_card
├── static/
│   ├── css/style.css       # Custom responsive stylesheet
│   └── js/main.js          # AJAX like/follow, compose helpers, toasts, mobile nav
├── manage.py
└── requirements.txt
```

---

## 🔗 Main URLs

| URL | Description |
|-----|-------------|
| `/` | Home feed (login required — anonymous users are sent to Explore) |
| `/explore/` | All posts, newest first |
| `/post/new/` | Create post (POST) |
| `/post/<id>/` | Post detail + comments |
| `/post/<id>/like/`, `/post/<id>/comment/`, `/post/<id>/delete/` | Post actions (POST) |
| `/accounts/u/<username>/` | User profile |
| `/accounts/u/<username>/follow/` | Follow / unfollow toggle (POST) |
| `/accounts/u/<username>/followers/`, `/following/` | Follow lists |
| `/accounts/profile/edit/` | Edit own profile |
| `/accounts/search/?q=` | People search |
| `/accounts/register/`, `/accounts/login/`, `/accounts/logout/` | Auth |
| `/admin/` | Django admin |

---

## 🧠 How it works (short notes)

- **Profiles** – a `post_save` signal on `User` creates the matching `Profile`, so every account (including ones created in the admin) always has one.
- **Follow model** – `Follow(follower, following)` with a `UniqueConstraint` (no duplicates) and a `CheckConstraint` (no self-follow). `user.following` / `user.followers` reverse relations give the lists and counts.
- **Feed query** – `Post.objects.filter(Q(author__in=following_ids) | Q(author=request.user))`, annotated with `Count("likes")`, `Count("comments")` and an `Exists()` sub-query for "did I like this?" so the whole feed page renders in ~10 SQL queries regardless of the number of posts.
- **AJAX interactions** – forms with `js-like` / `js-follow` classes are intercepted in `static/js/main.js`; the views detect the `X-Requested-With` header and return JSON. Without JavaScript the same forms still work with a normal redirect (progressive enhancement).
- **Security** – CSRF on every POST, `@login_required` + `@require_POST` on all mutating views, ownership checks before deleting posts/comments, password validators on sign-up.

---

## 📸 Screenshots

> Add your screenshots to a `screenshots/` folder and reference them here, e.g.
> `![Feed](screenshots/feed.png)`

---

## 👤 Author

Developed as part of the **CodeAlpha Full Stack Development Internship**.
