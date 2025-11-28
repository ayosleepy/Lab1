from django.contrib import admin
from .models import Question, Choice
from .models import UserProfile

class ChoiceInLine(admin.TabularInline):
    model = Choice
    extra = 3


class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInLine]


admin.site.register(Question, QuestionAdmin)

# Регистрируем модель UserProfile в админ-панели
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'birth_date']  # Что показывать в списке
    search_fields = ['user__username']     # Поиск по имени пользователя