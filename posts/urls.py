from django.urls import path

from . import views
# прошу прощения, вы не могли бы помочь узнать почему
# не работает логин, если запустить сервер
# вроде как с прошлого спринта ничего не менял и все работало #
urlpatterns = [
    path("", views.index, name="index"),
    path("group/<slug:slug>/", views.group_posts, name="group_posts"),
    path("new/", views.new_post, name="new_post"),
    path('<str:username>/', views.profile, name='profile'),
    path('<str:username>/<int:post_id>/', views.post_view, name='post'),
    path('<str:username>/<int:post_id>/edit/', views.post_edit,
         name='post_edit'
         ),
]
