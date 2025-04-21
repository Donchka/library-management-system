"""
URL configuration for the library management system.
"""

from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('books/', views.book_list, name='book_list'),
    path('books/add', views.add_book, name='add_book'),
    path('books/<int:book_id>/edit', views.edit_book, name='edit_book'),
    path('books/<int:book_id>/borrow/', views.borrow_book, name='borrow_book'),
    path('books/<int:book_id>/reserve/', views.reserve_book, name='reserve_book'),
    path('books/<int:book_id>/delete/', views.delete_book, name='delete_book'),
    path('loans/<int:loan_id>/return/', views.return_book, name='return_book'),
    path('my-loans/', views.my_loans, name='my_loans'),
    path('manage-loans/', views.manage_loans, name='manage_loans'),
    path('my-reservations/', views.my_reservations, name='my_reservations'),
    path('my-reservations/<int:reservation_id>/fulfill', views.fulfill_reservation, name='fulfill_reservation'),
    path('my-reservations/<int:reservation_id>/cancel', views.cancel_reservation, name='cancel_reservation'),
    path('manage-reservations/', views.manage_reservations, name='manage_reservations'),
    path('manage-reservations/<int:reservation_id>/cancel', views.cancel_reservation, name='manage_cancel_reservation'),
    path('manage-members', views.manage_members, name='manage_members'),
    path('manage-members/<int:member_id>/remove', views.remove_member, name='manage_members_remove'),
    path('manage-staff/', views.manage_staff, name='manage_staff'),
    path('manage-staff/register', views.register_staff, name='register_staff'),
    path('manage-staff/<int:staff_id>/resign', views.resign_staff, name='resign_staff'),
] 