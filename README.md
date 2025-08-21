# Library Management System

A **web-based Library Management System** built with the **Django framework** and **MySQL** as the database backend.  
This system provides a simple but concrete solution for managing a library’s resources, members, and operations.

## Features

- **User Features**
  - Browse and search book catalog
  - Member registration & login
  - Book checkout & loan
  - Book reservation

- **Admin / Staff Features**
  - Manage book catalog (add/update/delete)
  - Manage library members
  - Manage book loans and reservations
  - Staff member management & role-based access
    
## Tech Stack

- **Backend**: [Django](https://www.djangoproject.com/) (Python Web Framework)  
- **Frontend**: Django Templates (HTML, CSS, Bootstrap for styling)  
- **Database**: [MySQL](https://www.mysql.com/)

## Installation
### 1.Clone repository
```bash
git clone https://github.com/Donchka/library-management-system.git
cd library-management-system
```
### 2.Install dependencies
```bash
pip install -r requirements.txt
```
### 3.Create and update .env
```bash
touch .env
```
```bash
DB_NAME=[your_db_name]
DB_USER=[your_db_user_name]
DB_PASSWORD=[your_db_password]
DB_HOST=localhost (or db hosted on cloud)
DB_PORT=3306
```
### 4.Run migrations
```bash
python manage.py migrate
```

### 5.Start development server
```bash
python manage.py runserver
```

[Documentaton](https://docs.google.com/document/d/1Q2mq_q7b7rKa-lEiYW4FnQoGkUH91QVHTdZgJr7d1iY/edit?usp=sharing)
