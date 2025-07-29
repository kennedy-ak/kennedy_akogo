# Personal Portfolio & Blog

This is a personal portfolio website built with Django. It includes a project showcase, a blog, and a contact form.

## Features

*   **Project Showcase:** Display your projects with titles, descriptions, technologies used, and multiple images.
*   **Blog:** Write and publish blog posts using a rich text editor with image upload capabilities.
*   **Contact Form:** A functional contact form that saves messages to the database.
*   **Admin Panel:** Manage all content (projects, blog posts, contact messages) through the Django admin interface.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

*   Python 3.x
*   pip (Python package installer)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd personal_site
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the dependencies:**

    A `requirements.txt` file is not included in the project. You can create one with the necessary packages:
    ```bash
    pip freeze > requirements.txt
    ```
    The key dependencies are:
    *   `django`
    *   `pillow` (for image fields)
    *   `django-ckeditor`

    Install them manually if you don't have a `requirements.txt`:
    ```bash
    pip install django pillow django-ckeditor
    ```

4.  **Apply migrations:**
    ```bash
    python manage.py migrate
    ```

5.  **Create a superuser to access the admin panel:**
    ```bash
    python manage.py createsuperuser
    ```

6.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```

The application will be available at `http://127.0.0.1:8000/`.

## Usage

*   **Admin Panel:** Access the admin panel at `http://127.0.0.1:8000/admin` to manage your projects, blog posts, and view contact messages.
*   **Portfolio:** View your projects and blog on the main site.

## Project Structure

*   `personal_site/`: Main project directory.
    *   `settings.py`: Project settings.
    *   `urls.py`: Main URL configuration.
*   `portfolio/`: The main application for your portfolio.
    *   `models.py`: Database models for Project, BlogPost, etc.
    *   `views.py`: Application logic.
    *   `urls.py`: App-specific URLs.
    *   `templates/`: HTML templates.
    *   `static/`: CSS, JavaScript, and image files.
*   `media/`: Directory for user-uploaded files (project images, blog post images).
*   `db.sqlite3`: The SQLite database file.
