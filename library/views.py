from datetime import datetime, timedelta
from decimal import Decimal

import bcrypt
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from .decorators import login_required_custom
from .models import Book, Loan, Member, Reservation, Staff


def home(request):
    """
    Renders the home page of the library management system.
    """
    return render(request, 'library/home.html')

def register(request):
    """
    Handles member registration process.
    """
    if request.method == 'POST':
        # Extract form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        address = request.POST.get('address')
        contact = request.POST.get('contact')
        register_member_status = {}

        # Check if email already exists
        if Member.objects.filter(email=email).exists():
            register_member_status['register_member_failed'] = True
            return render(request, 'library/register.html', register_member_status)

        # Create new member with hashed password
        member = Member.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            credential=bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode(),
            address=address,
            contact=contact,
            date_joined=datetime.now().date()
        )
        if request.session.get('is_authenticated'):
            messages.success(request, 'Registration successful')
            return redirect('manage_members')
        messages.success(request, 'Registration successful. Please login.')
        return redirect('login')
    
    return render(request, 'library/register.html')

def login_view(request):
    """
    Handles user authentication for both members and staff.
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        login_status = {}

        if 'staffLogin' in request.POST:
            # Handle staff login
            try:
                staff = Staff.objects.get(email=email)
                if not bcrypt.checkpw(password.encode('utf-8'),staff.credential.encode('utf-8')):
                    login_status['login_failed'] = True
                    return render(request, 'library/login.html', login_status)
                
                # Set session variables for staff
                request.session['staff_id'] = staff.staff_id
                request.session['is_authenticated'] = True
                request.session['user_name'] = staff.first_name + " " + staff.last_name + "[" + staff.role + "]"
                request.session['is_staff'] = True
                request.session['is_admin'] = False
                if staff.role == 'Administrator':
                    request.session['is_admin'] = True
                messages.success(request, 'Login successful')
                return redirect('home')
            except Staff.DoesNotExist:
                login_status['login_failed'] = True
                return render(request, 'library/login.html', login_status)
        else:
            # Handle member login
            try:
                member = Member.objects.get(email=email)
                if not bcrypt.checkpw(password.encode('utf-8'),member.credential.encode('utf-8')):
                    login_status['login_failed'] = True
                    return render(request, 'library/login.html', login_status)
                
                # Set session variables for member
                request.session['member_id'] = member.member_id
                request.session['is_authenticated'] = True
                request.session['user_name'] = member.first_name+" "+member.last_name
                request.session['is_staff'] = False
                request.session['is_admin'] = False
                messages.success(request, 'Login successful')
                return redirect('home')
            except Member.DoesNotExist:
                login_status['login_failed'] = True
                return render(request, 'library/login.html', login_status)

    return render(request, 'library/login.html')

def logout_view(request):
    """
    Handles user logout by clearing session data.
    """
    request.session.flush()
    messages.success(request, 'Logged out successfully')
    return redirect('home')

def book_list(request):
    """
    Displays a list of books with optional search functionality.
    """
    query = request.GET.get('q', '')
    books = Book.objects.all()
    
    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(isbn__icontains=query)
        )
    
    return render(request, 'library/book_list.html', {'books': books})

@login_required_custom
def edit_book(request, book_id):
    """
    Handles editing of book information.
    """
    book = get_object_or_404(Book, book_id=book_id)

    if request.method == 'POST':
        # Extract and update book information
        title = request.POST.get('editTitle')
        author = request.POST.get('editAuthor')
        publisher = request.POST.get('editPublisher')
        year = request.POST.get('editYear')
        ISBN = request.POST.get('editISBN')
        genre = request.POST.get('editGenre')
        available = request.POST.get('editAvailable')

        if not year:
            year = None
        if not publisher:
            publisher = None

        book.title = title
        book.author = author
        book.publisher = publisher
        book.year = year
        book.isbn = ISBN
        book.genre = genre
        book.availability = available
        book.save()
        messages.success(request, 'Book information updated')
    return redirect('book_list')

@login_required_custom
def add_book(request):
    """
    Handles addition of new books to the library.
    """
    if request.method == 'POST':
        # Extract new book information
        title = request.POST.get('newTitle')
        author = request.POST.get('newAuthor')
        publisher = request.POST.get('newPublisher')
        year = request.POST.get('newYear')
        ISBN = request.POST.get('newISBN')
        genre = request.POST.get('newGenre')
        available = request.POST.get('newAvailable')

        # Validate input
        if not ISBN.isnumeric():
            messages.error(request, 'Invalid ISBN')
            return redirect('book_list')
        elif not year.isnumeric():
            messages.error(request, 'Invalid year of publish')
            return redirect('book_list')
        elif Book.objects.filter(isbn=ISBN).exists():
            messages.error(request, 'The book with this ISBN already exist')
            return redirect('book_list')

        if not year:
            year = None
        if not publisher:
            publisher = None

        # Create new book
        Book.objects.create(
            title=title,
            author=author,
            publisher=publisher,
            year=year,
            isbn=ISBN,
            genre=genre,
            availability=available
        )
        messages.success(request, f'New book successfully added {title}')
    return redirect('book_list')

@login_required_custom
def delete_book(request, book_id):
    """
    Handles deletion of books from the library.
    """
    book = get_object_or_404(Book, book_id=book_id)

    if Loan.objects.filter(book=book).exclude(return_date__isnull=False).exists():
        messages.error(request, f'Unable to remove the book {book.title} since there are pending book loans')
        return redirect('book_list')

    book.delete()
    messages.success(request, f'Successfully removed {book.title}')
    return redirect('book_list')

@login_required_custom
def borrow_book(request, book_id):
    """
    Handles book borrowing process.
    """
    if not request.session.get('is_authenticated'):
        return HttpResponseForbidden('You are not authenticated')

    book = get_object_or_404(Book, book_id=book_id)
    member_id = request.session.get('member_id')
    
    if not member_id:
        messages.error(request, 'Please login to borrow books')
        return redirect('login')
    
    if book.availability <= 0:
        messages.error(request, 'Book is not available for borrowing')
        return redirect('book_list')
    
    # Create new loan record
    member = get_object_or_404(Member, member_id=member_id)
    loan_date = datetime.now().date()
    due_date = loan_date + timedelta(days=14)  # 2 weeks loan period
    
    Loan.objects.create(
        member=member,
        book=book,
        loan_date=loan_date,
        due_date=due_date
    )
    
    # Update book availability
    book.availability -= 1
    book.save()
    
    messages.success(request, f'Successfully borrowed {book.title}')
    return redirect('my_loans')

@login_required_custom
def fulfill_reservation(request, reservation_id):
    """
    Handles fulfillment of book reservations.
    """
    reservation = get_object_or_404(Reservation, reservation_id=reservation_id)
    book_id = reservation.book.book_id
    result = borrow_book(request, book_id)
    reservation.status = 'confirmed'
    reservation.save()
    return redirect('my_loans')

@login_required_custom
def cancel_reservation(request, reservation_id):
    """
    Handles cancellation of book reservations.
    """
    reservation = get_object_or_404(Reservation, reservation_id=reservation_id)
    reservation.status = 'cancelled'
    reservation.save()
    if request.session.get('is_staff'):
        return redirect('manage_reservations')
    return redirect('my_reservations')

@login_required_custom
def return_book(request, loan_id):
    """
    Handles book return process and calculates fines if overdue.
    """
    loan = get_object_or_404(Loan, loan_id=loan_id)
    member_id = request.session.get('member_id')
    
    if loan.return_date:
        messages.error(request, 'This book has already been returned')
        return redirect('my_loans')
    
    # Set return date and calculate fine if overdue
    return_date = datetime.now().date()
    loan.return_date = return_date
    
    if return_date > loan.due_date:
        days_overdue = (return_date - loan.due_date).days
        loan.fine = Decimal(days_overdue) * Decimal('0.50')  # $0.50 per day
    
    loan.save()
    
    # Update book availability
    book = loan.book
    book.availability += 1
    book.save()
    
    messages.success(request, f'Successfully returned {book.title}')
    if request.session.get('is_staff'):
        return redirect('manage_loans')
    return redirect('my_loans')

@login_required_custom
def my_loans(request):
    """
    Displays list of books borrowed by the current member.
    """
    member_id = request.session.get('member_id')
    if not member_id:
        return redirect('login')
    
    member = get_object_or_404(Member, member_id=member_id)
    loans = Loan.objects.filter(member=member).order_by('-loan_date')
    return render(request, 'library/my_loans.html', {'loans': loans})

@login_required_custom
def manage_loans(request):
    """
    Displays all loans in the system (staff view).
    """
    loans = Loan.objects.all()
    return render(request, 'library/manage_loans.html', {'loans': loans})

@login_required_custom
def reserve_book(request, book_id):
    """
    Handles book reservation process.
    """
    book = get_object_or_404(Book, book_id=book_id)
    member_id = request.session.get('member_id')
    
    if not member_id:
        messages.error(request, 'Please login to reserve books')
        return redirect('login')
    
    member = get_object_or_404(Member, member_id=member_id)
    
    # Check for existing reservation
    if Reservation.objects.filter(book=book, member=member, status='pending').exists():
        messages.error(request, 'You have already reserved this book')
        return redirect('book_list')

    # Create new reservation
    Reservation.objects.create(
        member=member,
        book=book,
        reservation_date=datetime.now().date(),
        status='pending'
    )
    
    messages.success(request, f'Successfully reserved {book.title}')
    return redirect('my_reservations')

@login_required_custom
def my_reservations(request):
    """
    Displays list of reservations made by the current member.
    """
    member_id = request.session.get('member_id')
    if not member_id:
        return redirect('login')
    
    member = get_object_or_404(Member, member_id=member_id)
    reservations = Reservation.objects.filter(member=member).order_by('-reservation_date')
    return render(request, 'library/my_reservations.html', {'reservations': reservations})

@login_required_custom
def manage_reservations(request):
    """
    Displays all reservations in the system (staff view).
    """
    reservations = Reservation.objects.all()
    return render(request, 'library/manage_reservations.html', {'reservations': reservations})

@login_required_custom
def manage_members(request):
    """
    Displays all members in the system (staff view).
    """
    members = Member.objects.all()
    return render(request, 'library/manage_members.html', {'members': members})

@login_required_custom
def remove_member(request, member_id):
    """
    Handles member removal from the system.
    """
    member = get_object_or_404(Member, member_id=member_id)

    # Check for pending loans or reservations
    if Reservation.objects.filter(member=member, status='pending').exists() or Loan.objects.filter(member=member).exclude(return_date__isnull=False).exists():
        messages.error(request, f'Unable to remove {member.first_name + " " + member.last_name} since there are pending book loans or reservation for this member')
        return redirect('manage_members')
    member.delete()
    messages.success(request, f'Successfully removed {member.first_name + " " + member.last_name}')
    return redirect('manage_members')

@login_required_custom
def manage_staff(request):
    """
    Displays all staff members in the system (admin view).
    """
    staffs = Staff.objects.all()
    return render(request, 'library/manage_staffs.html', {'staffs': staffs})

@login_required_custom
def register_staff(request):
    """
    Handles staff member registration process.
    """
    if request.method == 'POST':
        # Extract new staff information
        first_name = request.POST.get('staffFirstName')
        last_name = request.POST.get('staffLastName')
        password = request.POST.get('staffPassword')
        role = request.POST.get('staffRole')
        contact = request.POST.get('staffContact')
        email = request.POST.get('staffEmail')

        # Check for existing email
        if Staff.objects.filter(email=email).exists():
            messages.error(request, 'Staff member with this email already exists')
            return redirect('manage_staff')

        # Create new staff member
        Staff.objects.create(
            first_name=first_name,
            last_name=last_name,
            role=role,
            credential=bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode(),
            contact=contact,
            email=email
        )
        messages.success(request, f'New staff enrolled {first_name+""+last_name}')
    return redirect('manage_staff')

@login_required_custom
def resign_staff(request, staff_id):
    """
    Handles staff member removal from the system.
    """
    staff = get_object_or_404(Staff, staff_id=staff_id)

    # Prevent removing last administrator
    if staff.role == 'Administrator' and Staff.objects.filter(role='Administrator').count() == 1:
        messages.error(request, "There must be at least one administrator in the staff team")
        return redirect('manage_staff')

    staff.delete()
    messages.success(request, f'Successfully removed {staff.first_name + " " + staff.last_name}')
    return redirect('manage_staff')

def some_protected_view(request):
    """
    Example of a protected view that requires authentication.
    """
    if not request.session.get('is_authenticated', False):
        return redirect('login')
