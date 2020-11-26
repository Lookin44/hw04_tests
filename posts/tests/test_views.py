from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group


class PostPagesTests(TestCase):
    """Проверяем работу view-функций"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Group.objects.create(
            title='test-group',
            slug='test-slug',
            description='test-description'
        )

    def setUp(self):
        """Создаем пользователей"""
        self.guest_client = Client()
        user = get_user_model()
        self.user = user.objects.create_user(
            username='test-author',
            password='123456'
        )
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            'index.html': reverse('index'),
            'post_new.html': reverse('new_post'),
            'group.html': reverse(
                'group',
                kwargs={'slug': 'test-slug'}
            ),
        }
        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

