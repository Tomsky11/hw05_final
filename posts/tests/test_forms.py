import datetime as dt
import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post

User = get_user_model()
tmp_media_root = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=tmp_media_root)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        author = User.objects.create_user(username='Test_user')
        pub_date = dt.datetime.now().date()
        group = Group.objects.create(
            title='Test_group', slug='Test_group_slug')
        cls.post = Post.objects.create(
            text='Тестовый текст',
            pub_date=pub_date,
            author=author,
            group=group
        )
        cls.form = PostForm()

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

    def test_create_post(self):
        '''Новый пост сохраняется и выполняется переадресация
        на главную страницу.
        '''
        post_count = Post.objects.count()
        group = Group.objects.get(title='Test_group')
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
        form_data = {
            'text': 'Новый тестовый текст',
            'group': group.id,
            'image': image
        }
        response = self.authorized_client.post(
            reverse('posts:new_post'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertRedirects(response, reverse('posts:index'))
        author = self.user
        self.assertTrue(
            Post.objects.filter(
                text='Новый тестовый текст',
                group=group.id,
                author=author,
                image='posts/small.gif'
            ).exists()
        )

    def test_edit_post(self):
        '''Отредактированный пост сохраняется и выполняется переадресация
        на страницу поста.
        '''
        post_count = Post.objects.count()
        group = Group.objects.get(title='Test_group')
        author = self.post.author
        post_id = self.post.id
        form_data = {
            'text': 'Тестовый текст 2',
            'group': group.id,
        }
        response = self.authorized_client_2.post(
            reverse('posts:post_edit',
                    kwargs={'username': author, 'post_id': post_id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), post_count)
        self.assertRedirects(
            response,
            reverse('posts:post',
                    kwargs={'username': author, 'post_id': post_id})
        )
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст 2',
                group=group.id,
                author=author,
            ).exists()
        )
