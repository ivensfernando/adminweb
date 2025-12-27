from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from src.api_main import api, api_auth

urlpatterns = [
    path("api/", api.urls),
    path("auth/", api_auth.urls),
    # path("api_auth/", api_jwt.urls),
    # path("api_pay/", api_stripe.urls),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
