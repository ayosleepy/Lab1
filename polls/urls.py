from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'polls'

urlpatterns = [
    # Главная страница опросов
    path('', views.index, name='index'),

    # Страницы опросов
    path('<int:question_id>/', views.detail, name='detail'),
    path('<int:question_id>/vote/', views.vote, name='vote'),
    path('<int:question_id>/results/', views.results, name='results'),

    # Регистрация и профиль
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('delete-profile/', views.delete_profile, name='delete_profile'),

    # Аутентификация
    path('login/', auth_views.LoginView.as_view(template_name='polls/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='polls:index'), name='logout'),
]