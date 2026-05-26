# LITReview - Book and Literature Article Review Application

LITReview is a web application developed with the Django framework that allows users to request and publish reviews for books or articles, and follow other users to stay updated on their reading activities.

---

## Key Features

* **Complete Authentication**: Secure sign-up and login pages. Access is restricted to authenticated users.
* **Activity Feed (Flux)**: A reverse-chronological activity feed displaying tickets and reviews from the logged-in user, users they follow, and reviews posted in response to their own tickets.
* **Review Requests (Tickets)**: Create, update, and delete tickets (with a title, description, and optional cover image).
* **Reviews**:
  * Publish reviews in response to an existing ticket.
  * Create a review from scratch (ticket + review created in a single step).
  * Update and delete your own reviews.
* **Subscription Management (Abonnements)**:
  * Search and follow other users by their username (with error validation if the user does not exist, is yourself, or is already followed).
  * List followed users with an instant unfollow ("Désabonner") option.
  * List followers (users who follow you).

---

## Local Installation and Setup

### Prerequisites

Make sure you have [Python 3](https://www.python.org/) installed on your machine.

### Step 1: Clone the repository and navigate to the project directory

```bash
cd /path/to/project/litrevue
```

### Step 2: Create a virtual environment

```bash
python3 -m venv env
```

### Step 3: Activate the virtual environment

* **On macOS / Linux**:

  ```bash
  source env/bin/activate

  ```
  
* **On Windows (Command Prompt)**:

  ```cmd
  env\Scripts\activate.bat

  ```

* **On Windows (PowerShell)**:

  ```powershell
  env\Scripts\Activate.ps1
  ```

### Step 4: Install the required dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Run migrations and initialize the database

The application uses a local **SQLite** database.
Apply the migrations to initialize the database schema:

```bash
python manage.py migrate
```

### Step 6: Start the development server

```bash
python manage.py runserver
```

You can now access the local application in your browser at: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## Site Management and Administration

### Create a Superuser (Django Admin)

To access the Django administration console at `/admin/`:

```bash
python manage.py createsuperuser
```

Follow the on-screen instructions to set a username, email address, and password for the administrator.

---

## Code Quality Check

The project is fully compliant with the PEP8 style guide. To check compliance, run:

```bash
flake8 reviews/ authentication/
```
