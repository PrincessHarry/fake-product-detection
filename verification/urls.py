from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),  # Landing page
    # path("home", home, name="home"),  # Verification page
    path("verify/", views.verify_product, name="verify-product"),
 
    
    path("report/", views.report, name="report"),  # Reporting feature
]
