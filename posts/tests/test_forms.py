from django.contrib.auth import get_user_model
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
        test_text = 'Тестовое создание поста'
        form_data = {
            'text': test_text,
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        post = Post.objects.first()
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(post.text, test_text)
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group, self.group)

    def test_edit_post(self):
        """Тестируем изменение поста."""
        test_text = 'Тестовое создание поста'
        test_text_edit = 'Измененый текст для тестового поста'
        post = Post.objects.create(
            text=test_text,
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
            'text': test_text_edit,
            'group': group_2.id,
        }
        response = self.authorized_client.post(
            reverse('post_edit', args=(self.user.username, post.id)),
            data=form_data,
            follow=True
        )
        post_edit = Post.objects.first()
        self.assertRedirects(
            response,
            reverse('post', args=(self.user.username, post.id))
        )
        self.assertEqual(Post.objects.count(), post_count)
        self.assertEqual(post_edit.text, test_text_edit)
        self.assertEqual(post_edit.author, self.user)
        self.assertEqual(post_edit.group, group_2)
