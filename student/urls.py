from student import views
from django.conf.urls import url

urlpatterns = [
    url(r'^$', views.stu_index, name='student'),
]
