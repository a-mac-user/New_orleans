from swing import views
from django.conf.urls import url

urlpatterns = [
    url(r'^$', views.swing_index, name='swing'),
]
