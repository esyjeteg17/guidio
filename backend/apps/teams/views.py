from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Team, TeamMember
from .serializers import TeamCreateSerializer, TeamMemberSerializer, TeamSerializer


class TeamViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return (
            Team.objects.filter(Q(owner=user) | Q(members__user=user))
            .distinct()
            .prefetch_related("members__user")
            .select_related("owner")
        )

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return TeamCreateSerializer
        return TeamSerializer

    def perform_create(self, serializer):
        team = serializer.save(owner=self.request.user)
        TeamMember.objects.create(team=team, user=self.request.user, role=TeamMember.Role.OWNER)

    @action(detail=True, methods=["post"], url_path="leave")
    def leave(self, request, pk=None):
        team = self.get_object()
        if team.owner_id == request.user.id:
            return Response(
                {"detail": "Владелец не может покинуть команду"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        TeamMember.objects.filter(team=team, user=request.user).delete()
        return Response({"detail": "Вы покинули команду"})

    @action(detail=False, methods=["post"], url_path="join")
    def join(self, request):
        token = request.data.get("invite_token")
        if not token:
            return Response({"detail": "invite_token required"}, status=400)
        team = get_object_or_404(Team, invite_token=token)
        member, created = TeamMember.objects.get_or_create(
            team=team, user=request.user,
            defaults={"role": TeamMember.Role.EDITOR},
        )
        return Response(TeamSerializer(team).data, status=201 if created else 200)

    @action(detail=True, methods=["get", "post"], url_path="members")
    def members(self, request, pk=None):
        team = self.get_object()
        if request.method == "GET":
            qs = team.members.select_related("user").all()
            return Response(TeamMemberSerializer(qs, many=True).data)
        user_id = request.data.get("user_id")
        role = request.data.get("role", TeamMember.Role.EDITOR)
        if not user_id:
            return Response({"detail": "user_id required"}, status=400)
        member, created = TeamMember.objects.get_or_create(
            team=team, user_id=user_id, defaults={"role": role},
        )
        return Response(TeamMemberSerializer(member).data, status=201 if created else 200)
