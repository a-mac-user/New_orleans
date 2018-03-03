from sales import views
from django.conf.urls import url

urlpatterns = [
    url(r'^$', views.sales_index, name='sales'),
    url(r'^change/(\d+)/$', views.customer_change, name="customer_change"),
    url(r'^customers/$', views.customers, name="customers"),
    url(r'^customers/change/(\d+)/$', views.customer_change, name="customer_change"),
    url(r'^customers/add/$', views.customer_add, name="customer_add"),
    url(r'^my_customers/$', views.my_customers, name="my_customers"),
    url(r'^sales_report/$', views.sales_report, name="sales_report"),
    url(r'^enrollment/(\d+)/$', views.enrollment, name="enrollment"),
    url(r'^enrollment/stu/(\d+)/$', views.stu_enrollment, name="stu_enrollment"),

]
