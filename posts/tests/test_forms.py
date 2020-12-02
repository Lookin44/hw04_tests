from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.test import Client, TestCase
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
        )
        # Создаем авторизированный аккаунт
        user = get_user_model()
        cls.user = user.objects.create_user(
            username='test-author',
            password='123456'
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)


class EditPostTest(DataBaseTests, TestCase):
    """Тестируем добовление и изменение поста."""
    def test_new_post(self):
        """Тестируем добовление поста."""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовое создание поста',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        post = get_object_or_404(Post)
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertEqual(post.text, 'Тестовое создание поста')
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group, self.group)

    def test_edit_post(self):
        """Тестируем изменение поста."""
        # Создаем тестовый пост
        post = Post.objects.create(
            text='Тестовый текст',
            author=self.user,
            group=self.group,
        )
        # Создаем тетсувую группу
        group_2 = Group.objects.create(
            title='test-group-2',
            slug='test_group_2',
        )
        post_count = Post.objects.count()
        form_data = {
            'text': 'Измененый текст',
            'group': group_2.id,
        }
        response = self.authorized_client.post(
            reverse('post_edit', args=(self.user.username, post.id)),
            data=form_data,
            follow=True
        )
        post_edit = get_object_or_404(Post)
        self.assertRedirects(
            response,
            reverse('post', args=(self.user.username, post.id))
        )
        self.assertEqual(Post.objects.count(), post_count)
        self.assertEqual(post_edit.text, 'Измененый текст')
        self.assertEqual(post_edit.author, self.user)
        self.assertEqual(post_edit.group, group_2)
