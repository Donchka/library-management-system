from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('books/', views.book_list, name='book_list'),
    path('books/<int:book_id>/borrow/', views.borrow_book, name='borrow_book'),
    path('loans/<int:loan_id>/return/', views.return_book, name='return_book'),
    path('my-loans/', views.my_loans, name='my_loans'),
    path('books/<int:book_id>/reserve/', views.reserve_book, name='reserve_book'),
    path('my-reservations/', views.my_reservations, name='my_reservations'),
] 