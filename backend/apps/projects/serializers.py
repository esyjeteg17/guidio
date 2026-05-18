from rest_framework import serializers

from apps.users.serializers import UserSerializer

from .models import Project


class ProjectSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    collaborators = UserSerializer(many=True, read_only=True)
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = (
            "id", "name", "description", "kind", "brief", "cover",
            "is_favorite", "is_archived", "archived_at", "team",
            "owner", "collaborators", "is_owner", "invite_token",
            "summary_payload", "summary_generated_at",
            "created_at", "updated_at",
        )
        read_only_fields = (
            "id", "owner", "collaborators", "is_owner", "invite_token",
            "summary_payload", "summary_generated_at",
            "archived_at", "created_at", "updated_at",
        )

    def get_is_owner(self, obj: Project) -> bool:
        user = self.context.get("request") and self.context["request"].user
        return bool(user and user.is_authenticated and obj.owner_id == user.id)
