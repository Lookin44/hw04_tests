from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
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
        # Создаем авторизированный аккаунт
        user = get_user_model()
        cls.user = user.objects.create_user(
            username='test-author',
            password='123456'
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        # Создаем тестовый пост
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
            id=1
        )


class EditPostTest(DataBaseTests, TestCase):
    def test_new_post(self):
        post_count = Post.objects.count()
        form_data = {
            'text': self.post.text,
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), post_count + 1)

    def test_edit_post(self):
        post_count = Post.objects.count()
        form_data = {
            'text': self.post.text,
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('post_edit', args=('test-author', 1)),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('post',
                                               args=('test-author', 1)))
        self.assertEqual(Post.objects.count(), post_count)
