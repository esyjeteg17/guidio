from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.ai.deepseek import DeepSeekError
from apps.fonts import services
from apps.fonts.models import Font
from apps.fonts.serializers import (
    ChatSearchRequestSerializer,
    ChatSearchResponseSerializer,
    FontSerializer,
)


class FontListView(generics.ListAPIView):
    queryset = Font.objects.all()
    serializer_class = FontSerializer


class FontDetailView(generics.RetrieveAPIView):
    queryset = Font.objects.all()
    serializer_class = FontSerializer


class ChatSearchView(APIView):
    def post(self, request):
        req = ChatSearchRequestSerializer(data=request.data)
        req.is_valid(raise_exception=True)
        try:
            result = services.chat_search(
                req.validated_data["message"],
                kept_font_id=req.validated_data.get("kept_font_id"),
                top_k=req.validated_data.get("top_k", 8),
            )
        except DeepSeekError as exc:
            return Response(
                {"detail": f"DeepSeek error: {exc}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        serializer = ChatSearchResponseSerializer(result, context={"request": request})
        return Response(serializer.data)
