"""
This module contains the admin configuration for the library management system.
"""

from django.contrib import admin

from .models import Book, Loan, Member, Reservation, Staff


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('member_id', 'first_name', 'last_name', 'email', 'date_joined')
    search_fields = ('first_name', 'last_name', 'email')
    list_filter = ('date_joined',)

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('book_id', 'title', 'author', 'publisher', 'year', 'availability')
    search_fields = ('title', 'author', 'isbn')
    list_filter = ('genre', 'year')

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('loan_id', 'member', 'book', 'loan_date', 'due_date', 'return_date', 'fine')
    search_fields = ('member__first_name', 'member__last_name', 'book__title')
    list_filter = ('loan_date', 'due_date', 'return_date')

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('reservation_id', 'member', 'book', 'reservation_date', 'status')
    search_fields = ('member__first_name', 'member__last_name', 'book__title')
    list_filter = ('status', 'reservation_date')

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('staff_id', 'first_name', 'last_name', 'role', 'email')
    search_fields = ('first_name', 'last_name', 'email')
    list_filter = ('role',)
