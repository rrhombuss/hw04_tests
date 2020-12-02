from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from posts.models import Group, Post


class URLAccessTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Group.objects.create(
            title='grouptitle',
            slug='groupslug'
        )

    def setUp(self):
        self.guest_client = Client()
        self.auth_client = Client()
        self.another_auth_client = Client()
        User = get_user_model()
        self.user = User.objects.create_user(username='adda')
        self.auth_client.force_login(self.user)
        self.another_user = User.objects.create_user(username='daad')
        self.another_auth_client.force_login(self.another_user)

        Post1 = self.auth_client.post(reverse('new_post'),
                                      data={
                                            'group': Group.objects.get(
                                             slug='groupslug'),
                                            'text': 'posttext'
                                             }
                                      )
        post_id = Post.objects.get(author='adda', text='posttext').id

    def test_url_access(self):
        urls = ['/', '/group/groupslug',
                '/new', '/adda', '/adda/<int:post_id>']
        for url in urls:
            with self.subTest():
                response = self.auth_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_unauth_redirect(self):
        response = self.guest_client.get('/new', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/new')

    def test_flatpages(self):
        response1 = self.guest_client.get('/about-us/')
        self.assertEqual(response1.status_code, 200)
        response2 = self.guest_client.get('/terms/')
        self.assertEqual(response2.status_code, 200)
        response3 = self.guest_client.get('/about-author/')
        self.assertEqual(response3.status_code, 200)
        response4 = self.guest_client.get('/about-spec/')
        self.assertEqual(response4.status_code, 200)

    def test_post_edit_accessablity(self):
        response1 = self.guest_client.get('/adda/<int:post_id>/edit',
                                          follow=True)
        self.assertRedirects(response1, '/auth/login')
        response2 = self.auth_client.get('/adda/<int:post_id>/edit',
                                         follow=True)
        self.assertEqual(response2.status_code, 200)
        response3 = self.another_auth_client.get('/adda/<int:post_id>/edit',
                                                 follow=True)
        self.assertRedirects(response3, '/adda/<int:post_id>')

    def test_templates_correct(self):
        templates_urls = {
            'templates/index.html': '/',
            'templates/group': '/group/groupslug',
            'templates/new_post': '/new',
            'templates/new_post': '/adda/<int:post_id>/edit',
        }
        for template, url in templates_urls.items():
            with self.subTest():
                response = self.auth_client.get(url)
                self.assertTemplateUsed(response, template)
