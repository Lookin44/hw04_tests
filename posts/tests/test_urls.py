from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from posts.models import Group


class StaticURLTests(TestCase):
    """Тестрируем URL"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Group.objects.create(
            title='test-group',
            slug='test_group',
            description='test-description'
        )

    def setUp(self):
        """Создаем пользователей"""
        self.guest_client = Client()
        user = get_user_model()
        self.user = user.objects.create_user(
            username='test-author',
            email='testauthor@mail.com',
            password='123456'
        )
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    # Проверяем работу страниц для неавторизированого пользователя
    def test_homepage(self):
        """Тестируем работу главной страницы"""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200,
                         'Главная страница не отображается')

    def test_group(self):
        """Тестируем работу страницы тестовой группы"""
        response = self.guest_client.get('/group/test_group/')
        self.assertEqual(response.status_code, 200,
                         'Страница тестовой группы не отображается')

    # Проверяем работу страниц для авторизированого пользователя
    def test_new_post(self):
        """Тестируем работу страницы создания нового поста"""
        response = self.authorized_client.get('/new/')
        self.assertEqual(response.status_code, 200,
                         'Страница создания нового поста не отображается')

    # Проверяем редиректы для неавторизованного пользователя
    def test_new_post_unauthorized(self):
        """Проверка редиректа неавторизированного пользователя"""
        response = self.guest_client.get('/new/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/new/')

    # Проверка вызываемых шаблонов для каждого адреса
    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'index.html': '/',
            'post_new.html': '/new/',
            'group.html': '/group/test_group/',
        }
        for template, url in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
