import datetime
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


# Модель поста для опросов
class Question(models.Model):
    question_text = models.CharField(max_length=200, verbose_name='текст вопроса')
    pub_date = models.DateTimeField('дата публикации')
    # Полное описание для детальной страницы
    description = models.TextField('полное описание', blank=True)
    # Краткое описание для главной страницы
    short_description = models.CharField('краткое описание', max_length=300, blank=True)
    # Изображение к посту
    image = models.ImageField('изображение', upload_to='questions/', blank=True, null=True)
    # Автор вопроса
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='автор')
    # Время жизни поста
    end_date = models.DateTimeField('окончание опроса', null=True, blank=True)

    # Проверка, опубликован ли вопрос недавно
    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)

    # Проверка, активен ли еще опрос
    def is_active(self):
        if self.end_date:
            return timezone.now() <= self.end_date
        return True  # Если end_date не указан, опрос всегда активен

    def __str__(self):
        return self.question_text


# Модель варианта ответа для опросов
class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='вопрос')
    choice_text = models.CharField(max_length=200, verbose_name='текст варианта')
    votes = models.IntegerField(default=0, verbose_name='голоса')
    # Поле для отслеживания проголосовавших пользователей
    voters = models.ManyToManyField(User, blank=True, related_name='votes', verbose_name='проголосовавшие')

    # Метод для добавления голоса с проверкой
    def add_vote(self, user):
        if user not in self.voters.all():
            self.votes += 1
            self.voters.add(user)
            self.save()
            return True
        return False

    # Метод для расчета процента голосов
    def get_percentage(self, total_votes):
        if total_votes > 0:
            return (self.votes / total_votes) * 100
        return 0

    def __str__(self):
        return self.choice_text


# Модель профиля пользователя
class UserProfile(models.Model):
    # Связь один-к-одному со встроенной моделью User
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='пользователь')
    # Аватар пользователя (обязательное поле)
    avatar = models.ImageField(upload_to='avatars/', verbose_name='аватар')
    # Дополнительные поля
    bio = models.TextField(max_length=500, blank=True, verbose_name='о себе')
    birth_date = models.DateField(null=True, blank=True, verbose_name='дата рождения')

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

    def __str__(self):
        return f'Профиль {self.user.username}'


# Сигнал для сохранения профиля при сохранении пользователя
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Сохраняем профиль, если он существует
    try:
        instance.userprofile.save()
    except UserProfile.DoesNotExist:
        # Профиль будет создан при первом обращении через get_or_create в views.py
        pass