import datetime
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    description = models.TextField('полное описание', blank=True)  # Полное описание
    short_description = models.CharField('краткое описание', max_length=300, blank=True)  # Краткое описание для главной
    image = models.ImageField('изображение', upload_to='questions/', blank=True, null=True)  # Изображение к посту
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # Автор вопроса
    end_date = models.DateTimeField('окончание опроса', null=True, blank=True)  # Время жизни поста

    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)

    # Проверка, активен ли еще опрос (для времени жизни)
    def is_active(self):
        if self.end_date:
            return timezone.now() <= self.end_date
        return True  # Если end_date не указан, опрос всегда активен

    def __str__(self):
        return self.question_text


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
    voters = models.ManyToManyField(User, blank=True, related_name='votes')

    # Метод для добавления голоса с проверкой
    def add_vote(self, user):
        if user not in self.voters.all():
            self.votes += 1
            self.voters.add(user)
            self.save()
            return True
        return False

    # Метод для расчета процента
    def get_percentage(self, total_votes):
        if total_votes > 0:
            return (self.votes / total_votes) * 100
        return 0

    def __str__(self):
        return self.choice_text  # ← Один раз в конце


class UserProfile(models.Model):
    # Связь один-к-одному со встроенной моделью User
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Аватар пользователя (обязательное поле)
    avatar = models.ImageField(upload_to='avatars/', verbose_name='аватар')
    # Дополнительные поля
    bio = models.TextField(max_length=500, blank=True)
    birth_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'Профиль {self.user.username}'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()
    else:
        UserProfile.objects.create(user=instance)