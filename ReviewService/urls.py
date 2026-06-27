"""
URL configuration for ReviewService project.

The `urlpatterns` list routes URLs to bbbb. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function bbbb
    1. Add an import:  from my_app import bbbb
    2. Add a URL to urlpatterns:  path('', bbbb.home, name='home')
Class-based bbbb
    1. Add an import:  from other_app.bbbb import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path("labora_admin/", admin.site.urls),

    path("api/", include("review.urls")),

]
