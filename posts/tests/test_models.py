from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.contrib.auth import get_user_model

from posts.models import Post, Group


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='testtest',
            slug='slug1'
        )

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='adda')
        self.auth_user = Client()
        self.auth_user.force_login(self.user)
        self.post = Post.objects.create(author=self.user,
                                        group=PostModelTest.group,
                                        text='posttext')

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        field_verboses = {
            'group': 'Группа',
            'text': 'Текст',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    self.post._meta.get_field(value).verbose_name, expected)
    # тут почему то ошибка 'posttext' != 'Текст', хотя группа проходит #

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        field_help_texts = {
            'group': 'Необязательно',
            'text': 'Обязательно'
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    self.post._meta.get_field(value).help_text, expected)

    def test_str_post(self):
        expected = self.post.text[:15]
        self.assertEquals(expected, 'Текст')

    def test_str_group(self):
        expected = PostModelTest.group.title
        self.assertEquals(expected, 'testtest')
