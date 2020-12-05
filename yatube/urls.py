from django.contrib import admin
from django.urls import include, path
from django.contrib.flatpages import views
from django.conf.urls import handler404, handler500

urlpatterns = [
    path('about-spec/',
         views.flatpage,
         {'url': '/about-spec/'},
         name='about_spec'),
    path('about-author/',
         views.flatpage,
         {'url': '/about-author/'},
         name='about_author'),
    path("auth/", include("users.urls")),
    path("auth/", include("django.contrib.auth.urls")),
    path('about/', include('django.contrib.flatpages.urls')),
    path("admin/", admin.site.urls),
    path("", include("posts.urls")),
]

handler404 = "posts.views.page_not_found" # noqa
handler500 = "posts.views.server_error" # noqa
