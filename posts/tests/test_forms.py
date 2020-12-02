from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, Group


class TestAddingPost(TestCase):
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
                                        group=TestAddingPost.group,
                                        text='posttext')
        self.post_id = self.post.id

    def test_added(self):
        post_count = Post.objects.count()
        form_data = {'text': 'posttext'}
        self.auth_user.post(
            reverse('posts:new_post'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), post_count+1)

    def test_edit_post(self):
        self.auth_user.post(
            reverse('post_edit',
                    kwargs={'username': 'adda', 'post_id': self.post_id}),
            data={'text': 'new_text'},
            follow=True
                            )
        text = self.post.text
        self.assertEqual(text, 'new_text')
