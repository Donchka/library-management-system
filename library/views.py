from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.db.models import Q
from .models import Member, Book, Loan, Reservation
from datetime import datetime, timedelta
from decimal import Decimal
from django.http import HttpResponseForbidden
from .decorators import login_required_custom

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
            credential=password,  # In production, use proper password hashing
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

        try:
            # Authenticate the user manually
            member = Member.objects.get(email=email, credential=password)
            # Store the member ID in the session
            request.session['member_id'] = member.member_id
            request.session['is_authenticated'] = True  # Custom flag for authentication
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
def return_book(request, loan_id):
    loan = get_object_or_404(Loan, loan_id=loan_id)
    member_id = request.session.get('member_id')
    
    if loan.member.member_id != member_id:
        messages.error(request, 'You can only return your own books')
        return redirect('my_loans')
    
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

def some_protected_view(request):
    if not request.session.get('is_authenticated', False):
        return redirect('login')
    # Your view logic here
