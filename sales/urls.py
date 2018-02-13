from sales import views
from django.conf.urls import url

urlpatterns = [
    url(r'^$', views.sales_index, name='sales'),
]
