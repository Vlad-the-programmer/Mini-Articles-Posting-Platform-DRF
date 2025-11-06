from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

from articles.urls import router as articles_router
# from comments.urls import router as comments_router
from likes.urls import router as likes_router


urlpatterns = [
    path("admin/", admin.site.urls),

    # Auth
    path('api/auth/', include('users.urls')),

    # API Schema
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]


urlpatterns += articles_router.urls
# urlpatterns += comments_router.urls
urlpatterns += likes_router.urls
