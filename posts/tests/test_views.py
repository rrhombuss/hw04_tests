from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, render_to_response
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.models import Group, Post


class TestTemplateView(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='grouptitle',
            slug='groupslug',
            description= 'groupdisc'
        )

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='adda')
        self.auth_user = Client()
        self.auth_user.force_login(self.user)

        self.post = Post.objects.create(author=self.user,
                                        group=TestTemplateView.group,
                                        text='posttext')
        self.post_id = self.post.id

    def test_templates_from_views(self):
        templates = {
            'index.html': reverse('index'),
            'new_post.html': reverse('new_post'),
            'group.html': reverse('group_posts',
                                       kwargs={'slug': 'groupslug'}),
                     }
        for template, rev_name in templates.items():
            with self.subTest(rev_name=rev_name):
                response = self.auth_user.get(rev_name)
                self.assertTemplateUsed(response, template)

    def test_context_index(self):
        response = self.auth_user.get(reverse('index'))
        post_text0 = response.context.get('page')[0].text
        post_group0 = response.context.get('page')[0].group
        paginator_count = response.context.get('page').count(self.post)
        difference = paginator_count < 15
        self.assertEqual(post_text0, 'posttext')
        self.assertEqual(post_group0, Group.objects.get(slug='groupslug'))
        self.assertTrue(difference)

    def test_context_group(self):
        response = self.auth_user.get(
            reverse('group_posts', kwargs={'slug': 'groupslug'})
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
            # 'django.forms.fields' has no attribute 'ForeignKey', 
            # это поле не проверять или  #
            'text':  forms.fields.CharField
        }
        for value, field in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, field)

    def test_context_profile(self):
        response = self.auth_user.get(reverse('profile',
                                      kwargs={'username': 'adda'}))
        count = response.context.get('count')
        author = response.context.get('author')
        post = response.context.get('posts')
        self.post.refresh_from_db()
        # не очень понимаю, зачем тут рефрешить, если никаких
        # изменений не было в аргументах поста
        # и я что как не пробовал не понял как проверить те ли посты 
        # передаются с контекстом данный вариант возвращает 
        # <QuerySet [<Post: posttext>]> != <QuerySet [<Post: posttext>]>#
        self.assertEqual(count, 1)
        self.assertEqual(author.username, 'adda')
        self.assertEqual(post, author.posts.all())

    def test_post_view(self):
        post_id = get_object_or_404(Post, author__username='adda',
                                    text='posttext').id
        response = self.auth_user.get(reverse('post',
                                              kwargs={'username': 'adda',
                                              'post_id': post_id}))
        author = response.context.get('author')
        post = response.context.get('post')
        self.post.refresh_from_db()
        self.assertEqual(author.username, 'adda')
        self.assertEqual(post, Post.objects.get(author__username='adda',
                                                text='posttext'))

    def test_appear_index_group(self):
        count = Post.objects.count()
        Post.objects.create(author=self.user,
                                        group=TestTemplateView.group,
                                        text='posttext')
        response1 = self.auth_user.get(reverse('index'))
        r1count = response1.context.get('post_list').count()
        response2 = self.auth_user.get(reverse('group_posts',
                                       kwargs={'slug': 'groupslug'}))
        r2count = response2.context.get('posts').count()


        self.assertEqual(count + 1, r1count)
        self.assertEqual(count + 1, r2count)
