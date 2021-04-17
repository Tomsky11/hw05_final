import datetime as dt

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        author = User.objects.create_user(username='Test_user')
        pub_date = dt.datetime.now().date()
        group = Group.objects.create(
            title='Test_group', slug='Test_group_slug'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            pub_date=pub_date,
            author=author,
            group=group,
        )
        cls.templates_url_names = {
            'posts/index.html': reverse('posts:index'),
            'group.html': reverse(
                'posts:group',
                kwargs={'slug': 'Test_group_slug'}
            ),
            'posts/new.html': reverse('posts:new_post'),
            'posts/profile.html': reverse(
                'posts:profile',
                kwargs={'username': 'Test_user'}
            ),
            'posts/post.html': reverse(
                'posts:post',
                kwargs={'username': 'Test_user', 'post_id': 1}
            )
        }
        post_kwargs = {'username': 'Test_user', 'post_id': 1}
        cls.url_name_post_edit = reverse('posts:post_edit', kwargs=post_kwargs)

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='TestUser')
        self.authorized_client = Client()
        self.authorized_client_2 = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_2.force_login(self.post.author)

    def test_pages_exists_at_desired_locations(self):
        '''Страницы доступны любому пользователю
        (index, group, profile, post).
        '''
        url_names = (
            reverse('posts:index'),
            reverse('posts:group', kwargs={'slug': 'Test_group_slug'}),
            reverse('posts:profile', kwargs={'username': 'Test_user'}),
            reverse('posts:post',
                    kwargs={'username': 'Test_user', 'post_id': 1})
        )
        for url_name in url_names:
            with self.subTest(url_name=url_name):
                response = self.guest_client.get(url_name)
                self.assertEqual(response.status_code, 200)

    def test_new_post_url_exists_at_desired_location_authorized(self):
        '''Страница new_post доступна авторизованному пользователю.'''
        response = self.authorized_client.get(reverse('posts:new_post'))
        self.assertEqual(response.status_code, 200)

    def test_new_post_url_redirect_anonymous_on_admin_login(self):
        '''Страница по адресу new_post перенаправит анонимного
        пользователя на страницу логина.
        '''
        response = self.guest_client.get(
            reverse('posts:new_post'),
            follow=True
        )
        self.assertRedirects(
            response, f"/auth/login/?next={reverse('posts:new_post')}")

    def test_post_edit_url_is_not_available_for_not_author(self):
        '''Страница post_edit недоступна не автору.'''
        responses = {self.guest_client.get(self.url_name_post_edit),
                     self.authorized_client.get(self.url_name_post_edit)}
        for response in responses:
            with self.subTest():
                self.assertEqual(response.status_code, 302)

    def test_post_edit_url_available_for_author(self):
        '''Страница post_edit доступна автору.'''
        response = self.authorized_client_2.get(self.url_name_post_edit)
        self.assertEqual(response.status_code, 200)

    def test_post_edit_url_redirect_authorised_not_author_on_post(self):
        '''Страница редактирования поста перенаправит авторизованного не автора
        на страницу просмотра поста.
        '''
        response = self.authorized_client.get(self.url_name_post_edit)
        post_url = reverse('posts:post',
                           kwargs={'username': 'Test_user', 'post_id': 1})
        self.assertRedirects(response, post_url)

    def test_post_edit_redirect_anonymous_on_admin_login(self):
        '''Страница по адресу post_edit перенаправит анонимного
        пользователя на страницу логина.
        '''
        response = self.guest_client.get(
            self.url_name_post_edit,
            follow=True
        )
        post_edit_url = reverse('posts:post_edit',
                                kwargs={'username': 'Test_user', 'post_id': 1})
        self.assertRedirects(response, f'/auth/login/?next={post_edit_url}')

    def test_urls_uses_correct_template(self):
        '''URL-адрес использует соответствующий шаблон.'''
        templates_url_names = self.templates_url_names
        for temlate, reverse_name in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, temlate)

    def test_post_edit_url_uses_correct_template(self):
        ''' Правильный шаблон для post_edit.'''
        response = self.authorized_client_2.get(self.url_name_post_edit)
        self.assertTemplateUsed(response, 'posts/new.html')

    def test_page_not_found_return_correct_status_code(self):
        ''' Сервер возвращает код 404, если страница не найдена.'''
        response = self.guest_client.get('/nonexistent/')
        self.assertEqual(response.status_code, 404)
