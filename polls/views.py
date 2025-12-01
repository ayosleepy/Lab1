from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Question, Choice, UserProfile
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm


# Главная страница - список активных опросов
def index(request):
    # Берем только активные опросы (у которых время жизни не истекло)
    active_questions = Question.objects.filter(
        end_date__gte=timezone.now()
    ) | Question.objects.filter(end_date__isnull=True)

    # Сортируем по дате публикации (новые сверху)
    active_questions = active_questions.order_by('-pub_date')

    return render(request, 'polls/index.html', {
        'questions': active_questions
    })


# Детальная страница опроса
def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    # Проверяем, активен ли еще опрос
    if not question.is_active():
        messages.warning(request, 'Этот опрос завершен!')

    # Проверяем, голосовал ли уже пользователь
    user_voted = False
    if request.user.is_authenticated:
        # Проверяем, есть ли у пользователя голос в вариантах этого вопроса
        user_voted = Choice.objects.filter(
            question=question,
            voters=request.user
        ).exists()

    return render(request, 'polls/detail.html', {
        'question': question,
        'user_voted': user_voted,
    })


# Обработка голосования
@login_required
def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    # Проверяем, активен ли опрос
    if not question.is_active():
        messages.error(request, 'Голосование завершено!')
        return redirect('polls:detail', question_id=question.id)

    try:
        # Получаем выбранный вариант
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Если вариант не выбран
        messages.error(request, 'Вы не выбрали вариант ответа!')
        return redirect('polls:detail', question_id=question.id)

    # Проверяем, голосовал ли уже пользователь
    if selected_choice.voters.filter(id=request.user.id).exists():
        messages.error(request, 'Вы уже голосовали в этом опросе!')
        return redirect('polls:detail', question_id=question.id)

    # Добавляем голос
    selected_choice.add_vote(request.user)
    messages.success(request, 'Ваш голос учтен!')

    return redirect('polls:results', question_id=question.id)


# Страница результатов
def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    # Считаем общее количество голосов
    total_votes = sum(choice.votes for choice in question.choice_set.all())

    # Добавляем процент для каждого варианта
    choices = []
    for choice in question.choice_set.all():
        percentage = choice.get_percentage(total_votes) if total_votes > 0 else 0
        choices.append({
            'choice': choice,
            'percentage': round(percentage, 1)
        })

    return render(request, 'polls/results.html', {
        'question': question,
        'choices': choices,
        'total_votes': total_votes,
    })


# Представление для регистрации
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Аккаунт {username} был создан! Теперь можно войти.')
            return redirect('polls:login')
    else:
        form = UserRegisterForm()
    return render(request, 'polls/register.html', {'form': form})


# Представление для профиля
@login_required
def profile(request):
    # Создаем профиль, если его нет (для старых пользователей)
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if created:
        messages.info(request, 'Для вас создан профиль. Заполните информацию.')

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=user_profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Ваш профиль был обновлен!')
            return redirect('polls:profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=user_profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'user_profile': user_profile,
    }
    return render(request, 'polls/profile.html', context)


# Удаление профиля
@login_required
def delete_profile(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        messages.success(request, 'Ваш профиль был удален.')
        return redirect('polls:index')

    return render(request, 'polls/delete_profile.html')