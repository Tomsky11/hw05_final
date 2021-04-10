import datetime as dt

from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        author = User.objects.create_user(username='Test_user')
        pub_date = dt.datetime.now().date()
        cls.group = Group.objects.create(title='Test_group', slug='Test_group')
        cls.post = Post.objects.create(
            text='Тестовый текст',
            pub_date=pub_date,
            author=author,
            group=cls.group,
        )

    def test_verbose_name(self):
        '''verbose_name полей text, group совпадает с ожидаемым.'''
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст публикации',
            'group': 'Сообщество'
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        '''help_text полей text, group совпадает с ожидаемым.'''
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Введите текст публикации',
            'group': 'Выберите группу'
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)

    def test_object_name_is_text_field(self):
        '''__str__  это срока для post - post.text, для group - group.title.'''
        post = PostModelTest.post
        group = PostModelTest.group
        object_names = {
            post: post.text,
            group: group.title
        }
        for object_name, expected in object_names.items():
            with self.subTest():
                self.assertEqual(expected, str(object_name))
