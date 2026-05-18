from rest_framework import serializers

from apps.fonts.models import Font, FontPair


class FontSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    google_stylesheet_url = serializers.SerializerMethodField()
    distance = serializers.FloatField(read_only=True, required=False)

    class Meta:
        model = Font
        fields = (
            "id",
            "name",
            "category",
            "role",
            "width",
            "usage_context",
            "theme",
            "character_mood",
            "style",
            "source",
            "link",
            "google_family",
            "file_url",
            "google_stylesheet_url",
            "embedding_text",
            "distance",
        )

    def get_file_url(self, obj: Font) -> str | None:
        if not obj.file:
            return None
        request = self.context.get("request")
        url = obj.file.url
        return request.build_absolute_uri(url) if request else url

    def get_google_stylesheet_url(self, obj: Font) -> str | None:
        if obj.source != Font.Source.GOOGLE_FONTS or not obj.google_family:
            return None
        family = obj.google_family.replace(" ", "+")
        return f"https://fonts.googleapis.com/css2?family={family}&display=swap"


class FontPairSerializer(serializers.ModelSerializer):
    heading = FontSerializer(read_only=True)
    body = FontSerializer(read_only=True)
    distance = serializers.FloatField(read_only=True, required=False)

    class Meta:
        model = FontPair
        fields = ("id", "heading", "body", "context", "distance")


class ChatSearchRequestSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=2000)
    kept_font_id = serializers.IntegerField(required=False, allow_null=True)
    top_k = serializers.IntegerField(required=False, default=8, min_value=1, max_value=30)


class ChatSearchResponseSerializer(serializers.Serializer):
    intent = serializers.CharField()
    rewrite = serializers.DictField()
    pairs = FontPairSerializer(many=True)
    fonts = FontSerializer(many=True)
    kept_font_id = serializers.IntegerField(allow_null=True)
