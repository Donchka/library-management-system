from django.db import models

# Create your models here.

class Member(models.Model):
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
