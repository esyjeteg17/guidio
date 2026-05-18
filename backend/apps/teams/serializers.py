from rest_framework import serializers

from apps.users.serializers import UserSerializer

from .models import Team, TeamMember


class TeamMemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = TeamMember
        fields = ("id", "user", "role", "joined_at")


class TeamSerializer(serializers.ModelSerializer):
    members = TeamMemberSerializer(many=True, read_only=True)
    owner = UserSerializer(read_only=True)
    members_count = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = (
            "id", "name", "description", "avatar", "owner",
            "invite_token", "members", "members_count", "created_at",
        )
        read_only_fields = ("id", "owner", "invite_token", "created_at")

    def get_members_count(self, obj):
        return obj.members.count()


class TeamCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ("name", "description", "avatar")
