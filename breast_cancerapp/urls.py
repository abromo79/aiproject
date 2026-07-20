from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", views.doctor, name="doctor_dashboard"),
    path("dashboard/", views.dashbord, name="predict_form"),
    path("predict/", views.predict, name="predict"),
    path("image-predict/", views.image_predict_form, name="image_predict_form"),
    path("image-predict/upload/", views.image_predict, name="image_predict"),
    path("login/", auth_views.LoginView.as_view(template_name='login.html'), name="login"),
    
    # Reports and Analytics
    path("reports/", views.reports_dashboard, name="reports_dashboard"),
    path("reports/risk-assessment/", views.risk_assessment_reports, name="risk_assessment_reports"),
    path("reports/image-analysis/", views.image_analysis_reports, name="image_analysis_reports"),
    path("reports/checkup-history/", views.checkup_history, name="checkup_history"),
    
    # PDF Export
    path("export/pdf/<str:report_type>/", views.export_pdf, name="export_pdf"),
    
    # System
    path("user-guide/", views.user_guide, name="user_guide"),
    path("logout/", views.logout_view, name="logout"),
    
    # Language Switching
    path("set-language/", views.set_language, name="set_language"),
]
