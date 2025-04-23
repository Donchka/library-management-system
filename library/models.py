"""
This module defines the database models for the library management system.
Each model represents a table in the database and defines the structure of the data.
"""

from django.db import models


class Member(models.Model):
    """
    Represents a library member with their personal information and credentials.
    
    Attributes:
        member_id (AutoField): Primary key for the member
        first_name (CharField): Member's first name
        last_name (CharField): Member's last name
        address (CharField): Member's address (optional)
        contact (CharField): Member's contact number (optional)
        email (EmailField): Member's email address (unique)
        date_joined (DateField): Date when the member joined the library
        credential (CharField): Hashed password for authentication
    """
    member_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    address = models.CharField(max_length=100, null=True, blank=True)
    contact = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(unique=True)
    date_joined = models.DateField()
    credential = models.CharField(max_length=255)

    class Meta:
        db_table = 'members'

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Book(models.Model):
    """
    Represents a book in the library's collection.
    
    Attributes:
        book_id (AutoField): Primary key for the book
        title (CharField): Title of the book
        author (CharField): Author of the book
        publisher (CharField): Publisher of the book (optional)
        year (IntegerField): Year of publication (optional)
        isbn (CharField): International Standard Book Number (unique)
        availability (IntegerField): Number of copies available
        genre (CharField): Genre/category of the book (optional)
    """
    book_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=100)
    publisher = models.CharField(max_length=100, null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)
    isbn = models.CharField(max_length=13, unique=True, default="1234567891234")
    availability = models.IntegerField(default=0)
    genre = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'books'

    def __str__(self):
        return self.title

class Loan(models.Model):
    """
    Represents a book loan transaction between a member and the library.
    
    Attributes:
        loan_id (AutoField): Primary key for the loan
        member (ForeignKey): Reference to the borrowing member
        book (ForeignKey): Reference to the borrowed book
        loan_date (DateField): Date when the book was borrowed
        due_date (DateField): Expected return date
        return_date (DateField): Actual return date (optional)
        fine (DecimalField): Fine amount for overdue books
    """
    loan_id = models.AutoField(primary_key=True)
    member = models.ForeignKey(Member, on_delete=models.CASCADE, db_column='member_id')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, db_column='book_id')
    loan_date = models.DateField()
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    fine = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        db_table = 'loans'

    def __str__(self):
        return f"Loan {self.loan_id} - {self.book.title}"

class Reservation(models.Model):
    """
    Represents a book reservation made by a member.
    
    Attributes:
        reservation_id (AutoField): Primary key for the reservation
        member (ForeignKey): Reference to the reserving member
        book (ForeignKey): Reference to the reserved book
        reservation_date (DateField): Date when the reservation was made
        status (CharField): Current status of the reservation (pending/confirmed/cancelled)
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]

    reservation_id = models.AutoField(primary_key=True)
    member = models.ForeignKey(Member, on_delete=models.CASCADE, db_column='member_id')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, db_column='book_id')
    reservation_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    class Meta:
        db_table = 'reservations'

    def __str__(self):
        return f"Reservation {self.reservation_id} - {self.book.title}"

class Staff(models.Model):
    """
    Represents a library staff member with their role and credentials.
    
    Attributes:
        staff_id (AutoField): Primary key for the staff member
        first_name (CharField): Staff's first name
        last_name (CharField): Staff's last name
        role (CharField): Staff's role in the library (optional)
        contact (CharField): Staff's contact number (optional)
        email (EmailField): Staff's email address (unique)
        credential (CharField): Hashed password for authentication
    """
    staff_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    role = models.CharField(max_length=50, null=True, blank=True)
    contact = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(unique=True, default="default@test.ca")
    credential = models.CharField(max_length=255)

    class Meta:
        db_table = 'staffs'

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
