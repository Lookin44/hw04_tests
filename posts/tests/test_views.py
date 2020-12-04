import datetime as dt

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
        cls.group = Group.objects.create(
            title='test-group',
            slug='test_group',
            description='test-description'
        )
        cls.group_two = Group.objects.create(
            title='test-group-2',
            slug='test_group_2',
            description='test-description for second group'
        )
        user = get_user_model()
        cls.user = user.objects.create_user(
            username='test-author',
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
            pub_date=dt.datetime.now()
        )
        cls.site_one = Site(pk=1, domain='example.com', name='example.com')
        cls.site_one.save()
        cls.about_author = FlatPage.objects.create(
            url='/about-author/', title='Об авторе', content='Начинающий'
        )
        cls.about_spec = FlatPage.objects.create(
            url='/about-spec/', title='Технологии',
            content='О технологиях'
        )
        cls.about_author.sites.add(cls.site_one)
        cls.about_spec.sites.add(cls.site_one)


@modify_settings(MIDDLEWARE={'append': 'django.contrib.flatpages.middleware'
                                       '.FlatpageFallbackMiddleware'})
class PostPagesTests(DataBaseTests, TestCase):
    """Проверяем работу view-функций"""

    def test_post_on_index(self):
        """Тестовый пост появился на странице index"""
        response = self.authorized_client.get(reverse('index'))
        self.assertEqual(len(response.context['page']), 1)

    def test_post_on_group(self):
        """Тестовый пост появился на странице group"""
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': self.group.slug})
        )
        self.assertEqual(len(response.context['page']), 1)

    def test_post_not_in_group(self):
        """Тестовый пост не появился на странице group_2"""
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': self.group_two.slug})
        )
        self.assertEqual(len(response.context['page']), 0)

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
        for i in range(20):
            Post.objects.create(
                text='Тестовый текст',
                author=self.user,
                group=self.group_two,
            )
        response = self.authorized_client.get(reverse('index'))
        test_posts = response.context.get('page')
        self.assertEqual(len(test_posts), 10)

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
            reverse('post_edit', args=(self.user.username, self.post.id))
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
        page_context = response.context['page'][0]
        context_test_expectation = {
            page_context.text: self.post.text,
            page_context.author: self.post.author,
            page_context.group: self.post.group,
        }
        for context, test_expectation in context_test_expectation.items():
            with self.subTest():
                self.assertEqual(context, test_expectation,
                                 'Шаблон index сформирован с'
                                 ' неправильным еонтекстом')

    def test_group_page_show_correct_context(self):
        """Шаблон group сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': self.group.slug}))
        page_context = response.context['page'][0]
        context_test_expectation = {
            page_context.text: self.post.text,
            page_context.author: self.post.author,
            page_context.group: self.post.group,
            page_context.pub_date: self.post.pub_date,
        }
        for context, test_expectation in context_test_expectation.items():
            with self.subTest():
                self.assertEqual(context, test_expectation,
                                 'Шаблон group сформирован с'
                                 ' неправильным контекстом')

    def test_profile_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('profile', kwargs={'username': self.user})
        )
        page_context = response.context['page'][0]
        author_context = response.context['author']
        context_test_expectation = {
            page_context.text: self.post.text,
            page_context.author: self.post.author,
            page_context.group: self.post.group,
            page_context.pub_date: self.post.pub_date,
            author_context: self.post.author,
        }
        for context, test_expectation in context_test_expectation.items():
            with self.subTest():
                self.assertEqual(context, test_expectation,
                                 'Шаблон profile сформирован с'
                                 ' неправильным контекстом')

    def test_post_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('post', args=(self.user, self.post.id))
        )
        author_context = response.context['author']
        post_context = response.context['post']
        context_test_expectation = {
            author_context: self.post.author,
            post_context.text: self.post.text,
            post_context.author: self.post.author,
            post_context.group: self.post.group,
            post_context.pub_date: self.post.pub_date,
        }
        for context, test_expectation in context_test_expectation.items():
            with self.subTest():
                self.assertEqual(context, test_expectation,
                                 'Шаблон profile сформирован с'
                                 ' неправильным контекстом')
