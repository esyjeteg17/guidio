import logging
from urllib.parse import urlparse

import requests
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, StreamingHttpResponse
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_GET
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ChatMessage, ChatSession
from .serializers import (
    ChatMessageSerializer,
    ChatSessionListSerializer,
    ChatSessionSerializer,
    SendMessageSerializer,
)
from .services import generate_reply
from .soniox import SonioxError, transcribe as soniox_transcribe

logger = logging.getLogger(__name__)

ALLOWED_PROXY_HOSTS = {"kaboompics.com", "www.kaboompics.com"}
PROXY_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)


@require_GET
@cache_control(public=True, max_age=86400)
def image_proxy(request):
    """Стримит картинку с whitelist-доменов в обход hotlink-protection.

    GET /api/ai/image-proxy/?url=https://kaboompics.com/cache_1/.../image.jpeg
    """
    url = request.GET.get("url", "").strip()
    if not url:
        return HttpResponseBadRequest("url required")
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return HttpResponseBadRequest("invalid scheme")
    if parsed.hostname not in ALLOWED_PROXY_HOSTS:
        return HttpResponseBadRequest("host not allowed")

    try:
        upstream = requests.get(
            url,
            headers={
                "User-Agent": PROXY_USER_AGENT,
                "Referer": f"{parsed.scheme}://{parsed.hostname}/",
                "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
            },
            stream=True,
            timeout=10,
        )
    except requests.RequestException as exc:
        logger.warning("image-proxy upstream failed: %s", exc)
        return HttpResponse(status=502)

    if upstream.status_code != 200:
        upstream.close()
        return HttpResponse(status=upstream.status_code)

    content_type = upstream.headers.get("Content-Type", "image/jpeg")
    if not content_type.startswith("image/"):
        upstream.close()
        return HttpResponseBadRequest("not an image")

    response = StreamingHttpResponse(
        upstream.iter_content(chunk_size=16 * 1024),
        content_type=content_type,
    )
    cl = upstream.headers.get("Content-Length")
    if cl:
        response["Content-Length"] = cl
    return response


class ChatSessionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = ChatSession.objects.filter(user=self.request.user).prefetch_related("messages")
        mode = self.request.query_params.get("mode")
        if mode:
            qs = qs.filter(mode=mode)
        project = self.request.query_params.get("project")
        if project:
            qs = qs.filter(project_id=project)
        return qs

    def get_serializer_class(self):
        if self.action == "list":
            return ChatSessionListSerializer
        return ChatSessionSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"], url_path="send")
    def send(self, request, pk=None):
        session = self.get_object()
        serializer = SendMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        filters = request.data.get("filters") or None
        assistant = generate_reply(
            session,
            serializer.validated_data["content"],
            filters=filters,
            request=request,
        )
        # `get_object()` returns a session whose `.messages` was prefetched in
        # `get_queryset()` — that cache does NOT include the user/assistant
        # messages just created by `generate_reply`. Re-fetch with a fresh
        # prefetch so the serializer sees the full conversation.
        session = (
            ChatSession.objects.prefetch_related("messages")
            .get(pk=session.pk)
        )
        return Response(
            {
                "message": ChatMessageSerializer(assistant).data,
                "session": ChatSessionSerializer(session).data,
            },
            status=status.HTTP_201_CREATED,
        )


class ChatMessageReactionView(viewsets.ViewSet):
    """PATCH /ai/messages/{id}/reaction/ — поставить или снять реакцию."""
    permission_classes = [IsAuthenticated]

    def partial_update(self, request, pk=None):
        try:
            msg = ChatMessage.objects.select_related("session").get(pk=pk, session__user=request.user)
        except ChatMessage.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        reaction = request.data.get("reaction")
        if reaction not in {None, "", "like", "dislike"}:
            return Response({"detail": "Invalid reaction."}, status=status.HTTP_400_BAD_REQUEST)

        msg.reaction = reaction or None
        msg.save(update_fields=["reaction"])
        return Response(ChatMessageSerializer(msg).data)


class QuickGenerateView(viewsets.ViewSet):
    """One-shot: создать сессию и сразу отправить первый промпт."""
    permission_classes = [IsAuthenticated]

    def create(self, request):
        mode = request.data.get("mode", "free")
        content = request.data.get("content", "")
        project_id = request.data.get("project")
        filters = request.data.get("filters") or None
        if not content:
            return Response({"detail": "content required"}, status=400)
        if mode not in {"fonts", "moodboard", "colors", "free"}:
            return Response({"detail": "invalid mode"}, status=400)
        # Внутри проекта — одна сессия на режим: переиспользуем уже существующую,
        # чтобы не плодить дубли при повторных «новых подборах» в том же проекте.
        session = None
        if project_id:
            session = (
                ChatSession.objects.filter(
                    user=request.user, mode=mode, project_id=project_id,
                )
                .order_by("-updated_at")
                .first()
            )
        if session is None:
            session = ChatSession.objects.create(
                user=request.user, mode=mode, project_id=project_id,
            )
        assistant = generate_reply(session, content, filters=filters, request=request)
        # Same reason as in `ChatSessionViewSet.send`: re-fetch with prefetch
        # so the serializer sees the user/assistant messages just created.
        session = (
            ChatSession.objects.prefetch_related("messages")
            .get(pk=session.pk)
        )
        return Response(
            {
                "session": ChatSessionSerializer(session).data,
                "message": ChatMessageSerializer(assistant).data,
            },
            status=status.HTTP_201_CREATED,
        )


class TranscribeView(APIView):
    """POST /api/ai/transcribe/ — multipart `audio` → текст из Soniox.

    Принимает короткие записи (< ~60s). Файл проксируется в Soniox с серверным
    ключом и возвращается распознанный текст. Ответ: {"text": "..."}.
    """

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    MAX_AUDIO_BYTES = 25 * 1024 * 1024  # 25 МБ — с запасом для ~5 минут webm/opus

    def post(self, request):
        api_key = getattr(settings, "SONIOX_API_KEY", "") or ""
        if not api_key:
            return Response({"detail": "SONIOX_API_KEY не настроен"}, status=503)
        upload = request.FILES.get("audio")
        if upload is None:
            return Response({"detail": "field 'audio' is required"}, status=400)
        if upload.size and upload.size > self.MAX_AUDIO_BYTES:
            return Response({"detail": "audio too large"}, status=413)
        audio_bytes = upload.read()
        if not audio_bytes:
            return Response({"detail": "empty audio"}, status=400)

        filename = getattr(upload, "name", "recording.webm") or "recording.webm"
        mime = getattr(upload, "content_type", "audio/webm") or "audio/webm"
        # Принимаем подсказку языка от клиента (по умолчанию ru/en).
        lang_param = request.data.get("language") or ""
        language_hints = (
            [s.strip() for s in lang_param.split(",") if s.strip()]
            if lang_param
            else ["ru", "en"]
        )

        try:
            text = soniox_transcribe(
                api_key=api_key,
                audio_bytes=audio_bytes,
                filename=filename,
                mime=mime,
                language_hints=language_hints,
            )
        except SonioxError as exc:
            logger.warning("Soniox transcribe failed: %s", exc)
            return Response({"detail": "Не удалось распознать аудио"}, status=502)

        return Response({"text": text})
