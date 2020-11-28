from django.contrib.auth import get_user_model
from django.test import TestCase
from posts.models import Group, Post


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        """Создаем объект Group"""
        super().setUpClass()
        Group.objects.create(
            title='A'*200,
            slug='test_group',
            description='Б'*200
        )
        cls.group = Group.objects.get()

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        group = GroupModelTest.group
        field_verboses = {
            'title': 'Название',
            'slug': 'Ссылка',
            'description': 'Описание'
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        group = GroupModelTest.group
        field_help_texts = {
            'title': 'Напишите название группы',
            'slug': 'Напишите латиницей ссылку',
            'description': 'Напишите описание группы'
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).help_text, expected)

    def test_object_name_is_title_fild(self):
        """В поле __str__ объекта group записано значение поля group.title."""
        group = GroupModelTest.group
        expected_object_name = group.title
        self.assertEquals(expected_object_name, str(group))


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        """Создаем объект Post"""
        User = get_user_model()
        cls.user = User.objects.create(
            username='test-author',
            password='123456'
        )
        cls.group = Group.objects.create(
            title='test-group',
            slug='test_group',
            description='test-description'
        )
        Post.objects.create(
            text='Test-text',
            pub_date='22.11.2020',
            author=cls.user,
            group=cls.group
        )
        cls.post = Post.objects.get()

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа'
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Опишите свои мысли',
            'pub_date': 'Добавьте дату публикации',
            'author': 'Кто автор',
            'group': 'Выберите группу'
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)

    def test_object_name_is_title_fild(self):
        """В поле __str__ объекта post записано значение поля post.title."""
        post = PostModelTest.post
        expected_object_name = post.text
        self.assertEquals(expected_object_name, str(post))
