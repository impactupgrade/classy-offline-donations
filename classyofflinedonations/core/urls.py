from django.conf.urls import url
from django.contrib.auth.views import LogoutView

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    url(r'^password-change/$', views.password_change, name='password_change'),
    url(r'^password-change-done/$', views.password_change_done, name='password_change_done'),
    url(r'^password-reset/$', views.password_reset, name='password_reset'),
    url(r'^password-reset-done/$', views.password_reset_done, name='password_reset_done'),
    url(r'^password-reset-confirm/(?P<uidb64>.+)/(?P<token>.+)/$', views.password_reset_confirm, name='password_reset_confirm'),
    url(r'^password-reset-complete/$', views.password_reset_complete, name='password_reset_complete'),
    url(r'^enable-user/$', views.enable_user, name='enable_user'),
    url(r'^donate/$', views.donate, name='donate'),
    url(r'^approve/$', views.approve, name='approve'),
    url(r'^unapprove/(?P<donation_id>[0-9]+)/$', views.unapprove, name='unapprove'),
]
