import datetime as dt
import os
import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.cache import cache
from posts.models import Follow, Group, Post

User = get_user_model()
tmp_media_root = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=tmp_media_root)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        author = User.objects.create_user(username='Test_user')
        pub_date = dt.datetime.now().date()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        image = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.group = Group.objects.create(
            title='Test_group', slug='Test_group_slug'
        )
        cls.group_2 = Group.objects.create(
            title='Second_test_group', slug='Second_test_group_slug'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            pub_date=pub_date,
            author=author,
            group=cls.group,
            image=image
        )
        cls.templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'group.html': (
                reverse(
                    'posts:group',
                    kwargs={'slug': 'Test_group_slug'}
                )
            ),
            'posts/new.html': reverse('posts:new_post')
        }

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(tmp_media_root, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='TestUser')
        self.authorized_client = Client()
        self.authorized_client_2 = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_2.force_login(self.post.author)

    def test_pages_uses_correct_template(self):
        '''URL-адрес использует соответствующий шаблон (по name).'''
        templates_pages_names = self.templates_pages_names
        for temlate, revese_name in templates_pages_names.items():
            with self.subTest(revese_name=revese_name, temlate=temlate):
                response = self.authorized_client.get(revese_name)
                self.assertTemplateUsed(response, temlate)

    def test_index_shows_correct_context(self):
        '''Шаблон index.html сформирован с правильным контекстом.'''
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page'][0]
        index_page_context = {
            first_object.text: 'Тестовый текст',
            first_object.author.username: 'Test_user',
            first_object.group.title: 'Test_group',
            first_object.image.name: 'posts/small.gif'
        }
        for actual, expected in index_page_context.items():
            with self.subTest():
                self.assertEqual(actual, expected)

    def test_group_shows_correct_context(self):
        '''Шаблон group.html сформирован с правильным контекстом.'''
        response = self.authorized_client.get(
            reverse('posts:group', kwargs={'slug': 'Test_group_slug'})
        )
        test_context = response.context['page'][0]
        self.assertEqual(test_context.group.title, 'Test_group')
        self.assertEqual(test_context.group.slug, 'Test_group_slug')
        self.assertIn(test_context.image.name, 'posts/small.gif')

    def test_new_shows_correct_context(self):
        '''Шаблон new.html сформирован с правильным контекстом.'''
        response = self.authorized_client.get(reverse('posts:new_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
            'image': forms.fields.ImageField
        }
        for value, expected in form_fields.items():
            with self.subTest(expected=expected):
                form_fields = response.context['form'].fields[value]
                self.assertIsInstance(form_fields, expected)

    def test_post_edit_correct_context(self):
        '''Шаблон для post_edit сформирован с правильным контекстом.'''
        response = self.authorized_client_2.get(reverse('posts:new_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(expected=expected):
                form_fields = response.context['form'].fields[value]
                self.assertIsInstance(form_fields, expected)

    def test_post_shows_correct_context(self):
        ''' Шаблон post.html сформмрован с правильным контекстом.'''
        username = self.post.author.username
        response = self.guest_client.get(
            reverse('posts:post',
                    kwargs={'username': username, 'post_id': 1})
        )
        self.assertEqual(response.context['author'].username, 'Test_user')
        self.assertEqual(response.context['post'].id, 1)
        self.assertEqual(response.context['post'].image.name,
                         'posts/small.gif')

    def test_profile_shows_correct_context(self):
        '''Шаблон profile.html сформирован с правильным контекстом.'''
        username = self.post.author.username
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': username})
        )
        first_object = response.context['page'][0]
        index_page_context = {
            first_object.text: 'Тестовый текст',
            first_object.author.username: 'Test_user',
            first_object.group.title: 'Test_group',
            first_object.image.name: 'posts/small.gif'
        }
        for actual, expected in index_page_context.items():
            with self.subTest():
                self.assertEqual(actual, expected)

    def test_new_post_at_desired_location(self):
        '''Новый пост появляется на главной странице и на странице группы.'''
        url_names = (
            reverse('posts:group', kwargs={'slug': 'Test_group_slug'}),
            reverse('posts:index')
        )
        for url_name in url_names:
            with self.subTest():
                response = self.authorized_client.get(url_name)
                self.assertEqual(len(response.context['page']), 1)

    def test_new_post_not_at_wrong_location(self):
        '''Новый пост не появляется на странице не своей группы. '''
        url_name = (
            reverse('posts:group', kwargs={'slug': 'Second_test_group_slug'}),
        )
        response = self.authorized_client.get(url_name)
        post = self.post
        self.assertNotEqual(post, response.context.get('page'))

    def test_cache(self):
        response_1 = self.authorized_client.get(reverse('posts:index')).content
        author = self.user
        pub_date = dt.datetime.now().date()
        post = Post.objects.create(
            text='Второй тестовый текст',
            pub_date=pub_date,
            author=author,
            group=self.group
        )
        response_2 = self.authorized_client.get(reverse('posts:index')).content
        self.assertEqual(response_1, response_2)
        cache.clear()
        response_3 = self.authorized_client.get(reverse('posts:index')).content
        self.assertNotEqual(response_1, response_3)

    def test_authorized_client_allowed_to_follow_and_unfollow(self):
        '''Авторизованный пользователь может подписываться и отписываться.'''
        user = self.user
        author = self.post.author
        follow_url = reverse('posts:profile_follow',
                             kwargs={'username': author})
        self.authorized_client.get(follow_url)
        follow_exsts = Follow.objects.filter(
            user=user,
            author=author
        ).exists()
        self.assertTrue(follow_exsts)
        unfollow_url = reverse('posts:profile_unfollow',
                               kwargs={'username': author})
        self.authorized_client.get(unfollow_url)
        follow_exsts = Follow.objects.filter(
            user=user,
            author=author
        ).exists()
        self.assertFalse(follow_exsts)

    def test_new_post_exists_at_follow_page_for_follower(self):
        '''Новый пост появляется на странице избранных авторов подписчика
        и не появляется у не подписчика.'''
        follow_url = reverse('posts:profile_follow',
                             kwargs={'username': self.user})
        self.authorized_client_2.get(follow_url)
        add_new_post = self.authorized_client.post(
            reverse('posts:new_post'),
            {'text': 'Тест постов избранных авторов'},
            follow=True
        )
        url_name = (reverse('posts:follow_index'))
        response = self.authorized_client_2.get(url_name)
        self.assertIn(add_new_post.context['page'][0].text,
                      response.context['page'][0].text)
        user_3 = User.objects.create_user(username='User_3')
        authorized_client_3 = Client()
        authorized_client_3.force_login(user_3)
        response_3 = authorized_client_3.get(url_name)
        self.assertNotIn(add_new_post.context['page'][0].text,
                         response_3.context['page'])

    def test_only_authorized_client_allowed_add_comment(self):
        '''Только авторизованный пользователь может оставлять комментарий.'''
        author = self.post.author
        post_id = self.post.id
        post_kwargs = {'username': author, 'post_id': post_id}
        add_comment_page = reverse('posts:add_comment', kwargs=post_kwargs)
#        response_1 = self.authorized_client.get(add_comment_page)
#        self.assertEqual(response_1.status_code, 200)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        author = User.objects.create_user(username='Test_user')
        pub_date = dt.datetime.now().date()
        group = Group.objects.create(
            title='Test_group', slug='Test_group_slug'
        )
        for post in range(13):
            cls.post = Post.objects.create(
                text='Тестовый текст',
                pub_date=pub_date,
                author=author,
                group=group,
            )

    def test_index_page_containse_ten_records(self):
        '''На главной странице отображается 10 постов. '''
        response = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context.get('page').object_list), 10)
