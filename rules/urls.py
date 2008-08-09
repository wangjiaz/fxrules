from django.conf.urls.defaults import *
from django.conf import settings
from rules.webconsole.views import login, home

urlpatterns = patterns('',
    # Example:
    # (r'^rules/', include('rules.foo.urls')),

  (r'^admin/', include('django.contrib.admin.urls')),

  (r'^login/$', login.login),
  (r'^home/$', home.home),
  (r'^$', home.home),
  (r'^newtrade/(\d+)/$', home.newtrade),
  (r'^closetrade/(\d+)/$', home.closetrade),
  (r'^rule/(\d+)/$', home.rulestat),
  (r'^savevalue/$', home.savevalue),
)

if settings.DEBUG:
  urlpatterns += patterns('',
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/Users/care/fxrules/rules/webconsole/static'}),
    )

