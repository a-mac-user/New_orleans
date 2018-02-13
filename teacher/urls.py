from teacher import views
from django.conf.urls import url

urlpatterns = [
    url(r'^$', views.teacher_index, name='teacher'),
]
