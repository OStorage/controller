from django.conf.urls import url
import views

urlpatterns = [
    url(r'^$', views.storlet_list),
    url(r'^(?P<storlet_id>[0-9]+)/?$', views.storlet_detail),
    url(r'^(?P<storlet_id>[0-9]+)/data/?$', views.StorletData.as_view()),
    url(r'^(?P<project>\w+)/deploy/?$', views.storlet_list_deployed),

    # Deploy to project container or object
    url(r'^(?P<project>\w+)/deploy/(?P<filter_id>[0-9]+)/?$', views.filter_deploy),
    url(r'^(?P<project>\w+)/(?P<container>[-\w]+)/deploy/(?P<filter_id>[0-9]+)/?$', views.filter_deploy),
    url(r'^(?P<project>\w+)/(?P<container>[-\w]+)/(?P<swift_object>[-\w]+)/deploy/(?P<filter_id>[0-9]+)/?$', views.filter_deploy),

    # Undeploy to project container or object
    url(r'^(?P<project>\w+)/undeploy/(?P<filter_id>[0-9]+)/?$', views.filter_undeploy),
    url(r'^(?P<project>\w+)/(?P<container>[-\w]+)/undeploy/(?P<filter_id>[0-9]+)/?$', views.filter_undeploy),
    url(r'^(?P<project>\w+)/(?P<container>[-\w]+)/(?P<swift_object>[-\w]+)/undeploy/(?P<filter_id>[0-9]+)/?$', views.filter_undeploy),

    url(r'^dependencies/?$', views.dependency_list),
    url(r'^dependencies/(?P<dependency_id>\w+)/?$', views.dependency_detail),
    url(r'^dependencies/(?P<dependency_id>\w+)/data/?$', views.DependencyData.as_view()),
    url(r'^dependencies/(?P<project>\w+)/deploy/?$', views.dependency_list_deployed),
    url(r'^dependencies/(?P<project>\w+)/deploy/(?P<dependency_id>\w+)/?$', views.dependency_deploy),
    url(r'^dependencies/(?P<project>\w+)/undeploy/(?P<dependency_id>\w+)/?$', views.dependency_undeploy),

    url(r'^slos/?$', views.slo_list),
    url(r'^slo/(?P<dsl_filter>[^/]+)/(?P<slo_name>[^/]+)/(?P<target>[^/]+)/?$', views.slo_detail)
]
