from django.contrib.auth import get_user_model
from django.shortcuts import render_to_response
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.models import Group, Post


class TestTemplateView(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Group.objects.create(
            title='grouptitle',
            slug='groupslug',
        )
        cls.group = Group.objects.get(slug='groupslug')

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='adda')
        self.auth_user = Client()
        self.auth_user.force_login(self.user)

        self.post = Post.objects.create(author=self.auth_user,
                                        group=TestTemplateView.group,
                                        text='posttext')
        self.post_id = self.post.id

    def test_templates_from_views(self):
        templates = {
            'templates/index': reverse('index'),
            'templates/new_post': reverse('new_post'),
            'templates/group': reverse('group_posts',
                                       kwargs={'slug': 'groupslug'}),
                     }
        for template, rev_name in templates.items():
            with self.subTest(rev_name=rev_name):
                response = self.auth_user.get(rev_name)
                self.assertTemplateUsed(response, template)

    def test_context_index(self):
        response = self.auth_user.get(reverse('index'))
        post_text0 = response.context.get('post_list')[0].text
        post_group0 = response.context.get('post_list')[0].group
        paginator_count = response.context.get('paginator').count()
        difference = paginator_count < 15
        self.assertEqual(post_text0, 'posttext')
        self.assertEqual(post_group0, Group.objects.get(slug='groupslug'))
        self.assertTrue(difference)

    def test_context_group(self):
        response = self.auth_user.get(
            reverse('group', kwargs={'slug': 'groupslug'})
            )
        self.assertEqual(response.context.get('group').title,
                         'grouptitle')
        self.assertEqual(response.context.get('group').description,
                         'groupdisc')

    def test_context_new(self):
        response = self.auth_user.get(reverse('new_post'))
        form_fields = {
            'group': forms.fields.ForeignKey,
            'text':  forms.fields.CharField
        }
        for value, field in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, field)

    def test_context_post_edit(self):
        response = self.auth_user.get(
            reverse('post_edit', kwargs={'username': 'adda',
                                         'post_id': self.post_id}
                    )
            )
        form_fields = {
            'group': forms.fields.ForeignKey,
            'text':  forms.fields.CharField
        }
        for value, field in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, field)

    def test_context_profile(self):
        response = self.auth_user.get(reverse('profile'))
        count = response.context.get('count')
        author = response.context.get('author')
        post = response.context.get('post_list')
        self.assertEqual(count, 1)
        self.assertEqual(author, 'adda')
        self.assertEqual(post, Post.objects.get(
            author='adda', id=self.post_id)
            )

    def test_post_view(self):
        post_id = Post.objects.get(author='adda', text='posttext').id
        response = self.auth_user.get(reverse('post',
                                              kwargs={'int': post_id}))
        author = response.context.get('author')
        post = response.context.get('post')
        self.assertEqual(author, 'adda')
        self.assertEqual(post, Post.objects.get(author='adda',
                                                text='posttext'))

    def test_appear_index_group(self):
        response1 = self.auth_user.get(
            'posts:index').context.get('post_list')[0]
        response2 = self.auth_user.get('posts:group').context.get('posts')[0]
        self.assertIsNotNone(response1)
        self.assertIsNotNone(response2)
