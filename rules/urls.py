from django.conf.urls.defaults import *
from rules.webconsole.views import login

urlpatterns = patterns('',
    # Example:
    # (r'^rules/', include('rules.foo.urls')),

    # Uncomment this for admin:
#     (r'^admin/', include('django.contrib.admin.urls')),

  (r'^login/$', login.login_page),
)
