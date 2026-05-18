from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    ChatMessageReactionView,
    ChatSessionViewSet,
    QuickGenerateView,
    TranscribeView,
    image_proxy,
)

router = DefaultRouter()
router.register(r"sessions", ChatSessionViewSet, basename="chat-sessions")

urlpatterns = router.urls + [
    path("generate/", QuickGenerateView.as_view({"post": "create"}), name="ai-generate"),
    path("messages/<int:pk>/reaction/", ChatMessageReactionView.as_view({"patch": "partial_update"}), name="ai-message-reaction"),
    path("image-proxy/", image_proxy, name="ai-image-proxy"),
    path("transcribe/", TranscribeView.as_view(), name="ai-transcribe"),
]
