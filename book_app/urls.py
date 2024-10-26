from . import views
from django.urls import path, include

urlpatterns = [
    path('', views.main_page, name='main-page'),
    path('registration', views.UserRegistrationView.as_view(), name='user-registration'),
    path('authorization', views.AuthorizationView.as_view(), name='user-authorization'),
    path('user_account', views.UserAccountView.as_view(), name='user-account'),
    path('library', views.show_all_books, name='library'),
    path('authors', views.show_all_authors, name='authors'),
    path('library/<slug:book_slug>', views.show_one_book, name='book-info'),
    path('authors/<slug:author_slug>', views.about_author, name='author-info'),
    path('account_recovery', views.AccountRecoveryView.as_view(), name='account-recovery'),
    path('reset_password', views.PasswordResetView.as_view(), name='reset-password'),
    path('set_new_password', views.SetNewPasswordView.as_view(), name='set-new-password'),
]