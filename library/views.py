from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.db.models import Q
from .models import Member, Book, Loan, Reservation, Staff
from datetime import datetime, timedelta
from decimal import Decimal
from django.http import HttpResponseForbidden
from .decorators import login_required_custom
import bcrypt

def home(request):
    return render(request, 'library/home.html')

def register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        address = request.POST.get('address')
        contact = request.POST.get('contact')

        if Member.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return redirect('register')

        member = Member.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            credential=bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode(),  # In production, use proper password hashing
            address=address,
            contact=contact,
            date_joined=datetime.now().date()
        )
        messages.success(request, 'Registration successful. Please login.')
        return redirect('login')
    
    return render(request, 'library/register.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if 'staffLogin' in request.POST:
            try:
                staff = Staff.objects.get(email=email)
                if not bcrypt.checkpw(password.encode('utf-8'),staff.credential.encode('utf-8')):
                    messages.error(request, 'Invalid credentials')
                    return render(request, 'library/login.html')
                # Store the member ID in the session
                request.session['staff_id'] = staff.staff_id
                request.session['is_authenticated'] = True  # Custom flag for authentication
                request.session['user_name'] = staff.first_name + " " + staff.last_name + "[" + staff.role + "]"
                request.session['is_staff'] = True
                request.session['is_admin'] = False
                if staff.role == 'Administrator':
                    request.session['is_admin'] = True
                messages.success(request, 'Login successful')
                return redirect('home')
            except Staff.DoesNotExist:
                messages.error(request, 'Invalid credentials')
        else:
            try:
                # Authenticate the user manually
                member = Member.objects.get(email=email)
                if not bcrypt.checkpw(password.encode('utf-8'),member.credential.encode('utf-8')):
                    messages.error(request, 'Invalid credentials')
                    return render(request, 'library/login.html')
                # Store the member ID in the session
                request.session['member_id'] = member.member_id
                request.session['is_authenticated'] = True  # Custom flag for authentication
                request.session['user_name'] = member.first_name+" "+member.last_name
                request.session['is_staff'] = False
                request.session['is_admin'] = False
                messages.success(request, 'Login successful')
                return redirect('home')
            except Member.DoesNotExist:
                messages.error(request, 'Invalid credentials')

    return render(request, 'library/login.html')

def logout_view(request):
    request.session.flush()  # Clear all session data
    messages.success(request, 'Logged out successfully')
    return redirect('home')

def book_list(request):
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
    book = get_object_or_404(Book, book_id=book_id)

    if request.method == 'POST':
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
    if request.method == 'POST':
        title = request.POST.get('newTitle')
        author = request.POST.get('newAuthor')
        publisher = request.POST.get('newPublisher')
        year = request.POST.get('newYear')
        ISBN = request.POST.get('newISBN')
        genre = request.POST.get('newGenre')
        available = request.POST.get('newAvailable')

        if not ISBN.isnumeric():
            messages.error(request, 'Invalid ISBN')
            return redirect('book_list')
        elif Book.objects.filter(isbn=ISBN).exists():
            messages.error(request, 'The book with this ISBN already exist')
            return redirect('book_list')

        if not year:
            year = None
        if not publisher:
            publisher = None

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
    book = get_object_or_404(Book, book_id=book_id)
    book.delete()
    messages.success(request, f'Successfully removed {book.title}')
    return redirect('book_list')

@login_required_custom
def borrow_book(request, book_id):
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
    
    member = get_object_or_404(Member, member_id=member_id)
    loan_date = datetime.now().date()
    due_date = loan_date + timedelta(days=14)  # 2 weeks loan period
    
    Loan.objects.create(
        member=member,
        book=book,
        loan_date=loan_date,
        due_date=due_date
    )
    
    book.availability -= 1
    book.save()
    
    messages.success(request, f'Successfully borrowed {book.title}')
    return redirect('my_loans')

@login_required_custom
def fulfill_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, reservation_id=reservation_id)
    book_id = reservation.book.book_id
    result = borrow_book(request, book_id)
    reservation.status = 'confirmed'
    reservation.save()
    return redirect('my_loans')

@login_required_custom
def cancel_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, reservation_id=reservation_id)
    reservation.status = 'cancelled'
    reservation.save()
    if request.session.get('is_staff'):
        return redirect('manage_reservations')
    return redirect('my_reservations')

@login_required_custom
def return_book(request, loan_id):
    loan = get_object_or_404(Loan, loan_id=loan_id)
    member_id = request.session.get('member_id')
    
    # if loan.member.member_id != member_id:
    #     messages.error(request, 'You can only return your own books')
    #     return redirect('my_loans')
    
    if loan.return_date:
        messages.error(request, 'This book has already been returned')
        return redirect('my_loans')
    
    return_date = datetime.now().date()
    loan.return_date = return_date
    
    # Calculate fine if overdue
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
    member_id = request.session.get('member_id')
    if not member_id:
        return redirect('login')
    
    member = get_object_or_404(Member, member_id=member_id)
    loans = Loan.objects.filter(member=member).order_by('-loan_date')
    return render(request, 'library/my_loans.html', {'loans': loans})

@login_required_custom
def manage_loans(request):
    loans = Loan.objects.all()
    return render(request, 'library/manage_loans.html', {'loans': loans})

@login_required_custom
def reserve_book(request, book_id):
    book = get_object_or_404(Book, book_id=book_id)
    member_id = request.session.get('member_id')
    
    if not member_id:
        messages.error(request, 'Please login to reserve books')
        return redirect('login')
    
    member = get_object_or_404(Member, member_id=member_id)
    
    # Check if already reserved
    if Reservation.objects.filter(book=book, member=member, status='pending').exists():
        messages.error(request, 'You have already reserved this book')
        return redirect('book_list')
    
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
    member_id = request.session.get('member_id')
    if not member_id:
        return redirect('login')
    
    member = get_object_or_404(Member, member_id=member_id)
    reservations = Reservation.objects.filter(member=member).order_by('-reservation_date')
    return render(request, 'library/my_reservations.html', {'reservations': reservations})

@login_required_custom
def manage_reservations(request):
    reservations = Reservation.objects.all()
    return render(request, 'library/manage_reservations.html', {'reservations': reservations})

@login_required_custom
def manage_members(request):
    members = Member.objects.all()
    return render(request, 'library/manage_members.html', {'members': members})

@login_required_custom
def remove_member(request, member_id):
    member = get_object_or_404(Member, member_id=member_id)

    if Reservation.objects.filter(member=member, status='pending').exists() or Loan.objects.filter(member=member).exclude(return_date__isnull=False).exists():
        messages.error(request, f'Unable to remove {member.first_name + " " + member.last_name} since there are pending book loans or reservation for this member')
        return redirect('manage_members')
    member.delete()
    messages.success(request, f'Successfully removed {member.first_name + " " + member.last_name}')
    return redirect('manage_members')

@login_required_custom
def manage_staff(request):
    staffs = Staff.objects.all()
    return render(request, 'library/manage_staffs.html', {'staffs': staffs})

@login_required_custom
def register_staff(request):
    if request.method == 'POST':
        first_name = request.POST.get('staffFirstName')
        last_name = request.POST.get('staffLastName')
        password = request.POST.get('staffPassword')
        role = request.POST.get('staffRole')
        contact = request.POST.get('staffContact')
        email = request.POST.get('staffEmail')

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
    staff = get_object_or_404(Staff, staff_id=staff_id)

    if staff.role == 'Administrator' and Staff.objects.filter(role='Administrator').count() == 1:
        messages.error(request, "There must be at least one administrator in the staff team")
        return redirect('manage_staff')

    staff.delete()
    messages.success(request, f'Successfully removed {staff.first_name + " " + staff.last_name}')
    return redirect('manage_staff')

def some_protected_view(request):
    if not request.session.get('is_authenticated', False):
        return redirect('login')
    # Your view logic here
