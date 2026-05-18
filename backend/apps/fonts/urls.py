from django.urls import path

from apps.fonts.views import ChatSearchView, FontDetailView, FontListView

app_name = "fonts"

urlpatterns = [
    path("", FontListView.as_view(), name="font-list"),
    path("<int:pk>/", FontDetailView.as_view(), name="font-detail"),
    path("chat-search/", ChatSearchView.as_view(), name="chat-search"),
]
