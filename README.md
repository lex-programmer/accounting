#  company_app — Django-проект для управления контрактами и фактурами

##  Запуск проекта

### 1. Установка Docker (рекомендуется)

Убедитесь, что Docker и Docker Compose установлены.

```bash
docker-compose up --build
docker-compose exec web python manage.py migrate

python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
python -m pip install --upgrade pip  # при необходимости
python manage.py migrate
python manage.py createsuperuser

# Сброс пароля суперпользователя (если нужно)

python manage.py shell
from django.contrib.auth.models import User
user = User.objects.get(username='admin')
user.set_password('новый_пароль')
user.save()
exit()

python manage.py runserver





