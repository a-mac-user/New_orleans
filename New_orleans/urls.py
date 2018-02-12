from swing import views
from django.contrib import admin
from django.conf.urls import url, include

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^entry', views.entry),
    url(r'^login$', views.acc_login),
    url(r'^logout', views.acc_logout),
    url(r'^swing/', include("swing.urls")),
    url(r'^teacher/', include("teacher.urls")),
    url(r'^student/', include("student.urls")),
    url(r'^sales/', include("sales.urls")),
]
