from swing import views
from django.conf.urls import url

urlpatterns = [
    url(r'^$', views.swing_index, name='swing'),
    url(r'^(\w+)/$', views.app_tables, name="app_tables"),  # 显示每个app里所有注册的表
    url(r'^(\w+)/(\w+)/$', views.display_table_list, name="table_list"),  # 显示每个表的数据
    url(r'^(\w+)/(\w+)/add/$', views.table_add, name="table_add"),
    url(r'^(\w+)/(\w+)/change/(\d+)/$', views.table_change, name="table_change"),
    url(r'^(\w+)/(\w+)/delete/(\d+)/$', views.table_del, name="table_del"),
]
