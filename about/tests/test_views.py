from django.test import Client, TestCase
from django.urls import reverse


class AboutViewsTest(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.templates_pages_names = {
            'about/author.html': reverse('about:author'),
            'about/tech.html': reverse('about:tech'),
        }

    def test_about_at_desired_location(self):
        '''Страницы /about/author/ и /about/tech/ доступны
        неавторизованному пользователю.
        '''
        templates_pages_names = self.templates_pages_names
        for url_name in templates_pages_names.values():
            with self.subTest():
                response = self.guest_client.get(url_name)
                self.assertEqual(response.status_code, 200)

    def test_about_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон (по name)."""
        templates_pages_names = self.templates_pages_names
        for template_name, url_name in templates_pages_names.items():
            with self.subTest():
                response = self.guest_client.get(url_name)
                self.assertTemplateUsed(response, template_name)
