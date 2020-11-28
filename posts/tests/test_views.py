from django import forms
from django.contrib.auth import get_user_model
from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site
from django.test import Client, TestCase, modify_settings
from django.urls import reverse

from posts.models import Group, Post


class DataBaseTests(TestCase):
    """Подготавливаем БД."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем тетсувую группу
        cls.group = Group.objects.create(
            title='test-group',
            slug='test_group',
            description='test-description'
        )
        # Создаем тетсувую группу
        cls.group_2 = Group.objects.create(
            title='test-group-2',
            slug='test_group_2',
            description='test-description for second group'
        )
        # Создаем авторизированный аккаунт
        user = get_user_model()
        cls.user = user.objects.create_user(
            username='test-author',
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        # Стоздаем тестовый пост
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
        )
        cls.site1 = Site(pk=1, domain='example.com', name='example.com')
        cls.site1.save()
        cls.about_author = FlatPage.objects.create(
            url='/about-author/', title='Об авторе', content='Начинающий'
        )
        cls.about_spec = FlatPage.objects.create(
            url='/about-spec/', title='Технологии',
            content='О технологиях'
        )
        cls.about_author.sites.add(cls.site1)
        cls.about_spec.sites.add(cls.site1)


@modify_settings(MIDDLEWARE={'append': 'django.contrib.flatpages.middleware'
                                       '.FlatpageFallbackMiddleware'})
class PostPagesTests(DataBaseTests, TestCase):
    """Проверяем работу view-функций"""

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        names_templates_page = {
            reverse('index'): 'index.html',
            reverse('new_post'): 'post_new.html',
            reverse('group', kwargs={'slug': 'test_group'}): 'group.html',
            reverse('post_edit', args=('test-author', 1)): 'post_new.html',

        }
        for reverse_name, template in names_templates_page.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_on_index(self):
        response = self.authorized_client.get(reverse('index'))
        self.assertEqual(len(response.context['page']), 1)

    def test_post_on_group(self):
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': 'test_group'})
        )
        self.assertEqual(len(response.context['page']), 1)

    def test_post_not_in_group(self):
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': 'test_group_2'})
        )
        self.assertEqual(len(response.context['page']), 0)

    def test_post_new_page_show_correct_context(self):
        """Шаблон post_new сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('post_edit', args=('test-author', 1))
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('index'))
        text = response.context.get('page')[0].text
        author = response.context.get('page')[0].author
        group = response.context.get('page')[0].group
        self.assertEqual(text, 'Тестовый текст')
        self.assertEqual(author, self.user)
        self.assertEqual(group, self.group)

    def test_group_page_show_correct_context(self):
        """Шаблон group сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': 'test_group'}))
        text = response.context.get('page')[0].text
        author = response.context.get('page')[0].author
        group = response.context.get('page')[0].group
        self.assertEqual(text, 'Тестовый текст')
        self.assertEqual(author, self.user)
        self.assertEqual(group, self.group)

    def test_profile_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('profile', kwargs={'username': 'test-author'})
        )
        profile = response.context.get('profile')
        post_count = response.context.get('posts_count')
        text = response.context.get('page')[0].text
        author = response.context.get('page')[0].author
        group = response.context.get('page')[0].group
        self.assertEqual(profile.username, self.user.username)
        self.assertEqual(post_count, 1)
        self.assertEqual(text, 'Тестовый текст')
        self.assertEqual(author, self.user)
        self.assertEqual(group, self.group)

    def test_post_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('post', args=('test-author', 1))
        )
        profile = response.context.get('profile')
        post_count = response.context.get('posts_count')
        text = response.context.get('post').text
        author = response.context.get('post').author
        group = response.context.get('post').group
        self.assertEqual(profile.username, self.user.username)
        self.assertEqual(post_count, 1)
        self.assertEqual(text, 'Тестовый текст')
        self.assertEqual(author, self.user)
        self.assertEqual(group, self.group)

    def test_author_flatpage_show_correct_context(self):
        response = self.authorized_client.get(reverse('about_author'))
        title = response.context.get('flatpage').title
        content = response.context.get('flatpage').content
        self.assertEqual(title, 'Об авторе')
        self.assertEqual(content, 'Начинающий')

    def test_spec_flatpage_show_correct_context(self):
        response = self.authorized_client.get(reverse('about_spec'))
        title = response.context.get('flatpage').title
        content = response.context.get('flatpage').content
        self.assertEqual(title, 'Технологии')
        self.assertEqual(content, 'О технологиях')

    def test_paginator(self):
        """В index передаеться не более 10 постов"""
        # Создаем несколько постов циклом
        posts = list()
        for i in range(20):
            posts.append(Post.objects.create(
                text='Тестовый текст',
                author=self.user,
                group=self.group_2,
            ))
        response = self.authorized_client.get(reverse('index'))
        post = response.context.get('page')
        self.assertEqual(len(post), 10)
