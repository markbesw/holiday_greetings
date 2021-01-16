
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('home', views.home),
    path('login_reg', views.login_reg),
    path('create_user', views.register),
    path('login', views.login),
    path('cards/recent', views.recent),
    path('cards/trending', views.trending),
    path('cards/a-z', views.a_z),
    path('cards/mycards', views.my_cards),
    path('create', views.create),
    path('logout', views.logout),
    path('create/<int:img_id>', views.image_details),
    path('granted/<int:item_id>', views.granted),
    path('search', views.search),
    path('test', views.send_email),
    path('upload', views.upload_image),
    path('review/<int:img_id>', views.review),
    path('view_card/<int:card_id>', views.view_card),
    path('view_card/<str:unique>/<int:card_id>', views.visitor_card),
    path('send_email/<int:card_id>', views.send_email),
    path('edit_card/<int:card_id>', views.edit_card),
    path('update/<int:card_id>', views.update_card),
    path('like/<int:card_id>', views.add_like),
    path('create_comment', views.create_comm),
]
