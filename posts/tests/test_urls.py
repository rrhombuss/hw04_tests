from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from posts.models import Group, Post


class URLAccessTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='grouptitle',
            slug='groupslug'
        )

    def setUp(self):
        User = get_user_model()
        self.guest_client = Client()
        self.auth_client = Client()
        self.another_auth_client = Client()
        self.user = User.objects.create_user(username='adda')
        self.auth_client.force_login(self.user)
        self.another_user = User.objects.create_user(username='daad')
        self.another_auth_client.force_login(self.another_user)

        self.post = Post.objects.create(author=self.user,
                                        group=URLAccessTests.group,
                                        text='posttext')

    def test_url_access(self):
        urls = [reverse('index'),
                reverse('group_posts', kwargs={'slug': 'groupslug'}),
                reverse('new_post'),
                reverse('profile', kwargs={'username': 'adda'}),
                reverse('post', kwargs={'username': 'adda', 'post_id': self.post.id})]
        for url in urls:
            with self.subTest():
                response = self.auth_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_unauth_redirect(self):
        response = self.guest_client.get(reverse('new_post'), follow=True)
        self.assertRedirects(response, '/auth/login/?next=/new/')

    def test_flatpages(self):
        response3 = self.guest_client.get(reverse('about-author'))
        self.assertEqual(response3.status_code, 200)
        response4 = self.guest_client.get(reverse('about-spec'))
        self.assertEqual(response4.status_code, 200)

    def test_post_edit_accessablity(self):
        response1 = self.guest_client.get(
            reverse('post_edit', kwargs={'username': 'adda', 'post_id': self.post.id}),
                                          follow=True)
        self.assertRedirects(response1, '/auth/login/?next=/adda/1/edit/')
        response2 = self.auth_client.get(
            reverse('post_edit', kwargs={'username': 'adda', 'post_id': self.post.id}),
                                         follow=True)
        self.assertEqual(response2.status_code, 200)
        response3 = self.another_auth_client.get(
            reverse('post_edit', kwargs={'username': 'adda', 'post_id': self.post.id}),
                                                 follow=True)
        self.assertRedirects(response3, reverse('post',
                                                kwargs={'username': 'adda',
                                                'post_id': self.post.id}))

    def test_templates_correct(self):
        templates_urls = {
            'index.html': reverse('index'),
            'group.html': reverse('group_posts', kwargs={'slug': 'groupslug'}),
            'new_post.html': reverse('new_post'),
            'edit_post.html': reverse('post_edit', 
                                      kwargs={'username': 'adda',
                                     'post_id': self.post.id}),
        }
        for template, url in templates_urls.items():
            with self.subTest():
                response = self.auth_client.get(url)
                self.assertTemplateUsed(response, template)
