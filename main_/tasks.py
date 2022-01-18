from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import send_mail


@shared_task
def adding_task(x, y):
    return x + y


@shared_task
def send_new_series():
    user = get_user_model().objects.all()
    user = [str(user[i]) for i in range(len(user))]
    user.remove('ata6ek@gmail.com')
    print(user)
    text = f'Вышел новый фильм'
    send_mail('Уведомление',
              text,
              'test@gmail.com',
              user)
    return text
