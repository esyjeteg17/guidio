from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.ai.deepseek import DeepSeekError
from apps.ai.services import summarise_project

from .models import Project
from .serializers import ProjectSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Project.objects.filter(
            Q(owner=user)
            | Q(collaborators=user)
            | Q(team__members__user=user)
            | Q(team__owner=user)
        ).distinct()

        scope = self.request.query_params.get("scope")
        if scope == "personal":
            qs = qs.filter(owner=user, team__isnull=True)
        elif scope == "team":
            qs = qs.filter(team__isnull=False)
        elif scope == "shared":
            qs = qs.filter(collaborators=user).exclude(owner=user)
        elif scope == "archived":
            qs = qs.filter(is_archived=True)

        kind = self.request.query_params.get("kind")
        if kind:
            qs = qs.filter(kind=kind)

        favorite = self.request.query_params.get("favorite")
        if favorite in ("1", "true"):
            qs = qs.filter(is_favorite=True)

        # Archived projects are excluded by default ТОЛЬКО в списке — иначе detail-эндпоинты
        # (retrieve / unarchive / summary / etc.) не смогли бы открывать архивный проект и
        # отдавали бы 404 после архивации.
        if self.action == "list":
            archived = self.request.query_params.get("archived")
            if scope != "archived" and archived not in ("1", "true", "all"):
                qs = qs.filter(is_archived=False)
        return qs

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["post"], url_path="summary")
    def summary(self, request, pk=None):
        project = self.get_object()
        try:
            payload = summarise_project(project)
        except DeepSeekError as exc:
            return Response(
                {"detail": f"AI недоступен: {exc}"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        return Response(
            {
                "summary_payload": payload,
                "summary_generated_at": project.summary_generated_at,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"], url_path="join")
    def join(self, request):
        """Join a project by its invite token — becomes a collaborator."""
        token = request.data.get("invite_token")
        if not token:
            return Response({"detail": "invite_token required"}, status=400)
        # Look up outside the limited queryset so invited users can also find it.
        project = get_object_or_404(Project, invite_token=token)
        user = request.user
        if project.owner_id == user.id:
            return Response(ProjectSerializer(project, context={"request": request}).data)
        already = project.collaborators.filter(pk=user.id).exists()
        if not already:
            project.collaborators.add(user)
        return Response(
            ProjectSerializer(project, context={"request": request}).data,
            status=status.HTTP_201_CREATED if not already else status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="rotate-invite")
    def rotate_invite(self, request, pk=None):
        """Owner can regenerate the invite token (invalidating old links)."""
        project = self.get_object()
        if project.owner_id != request.user.id:
            return Response({"detail": "Только владелец может менять ссылку"}, status=403)
        from .models import _project_invite_token
        project.invite_token = _project_invite_token()
        project.save(update_fields=["invite_token", "updated_at"])
        return Response({"invite_token": project.invite_token})

    @action(detail=True, methods=["delete"], url_path=r"collaborators/(?P<user_id>\d+)")
    def remove_collaborator(self, request, pk=None, user_id=None):
        project = self.get_object()
        if project.owner_id != request.user.id and str(request.user.id) != str(user_id):
            return Response({"detail": "Нельзя удалять других соавторов"}, status=403)
        project.collaborators.remove(user_id)
        return Response(status=204)

    @action(detail=True, methods=["post"], url_path="archive")
    def archive(self, request, pk=None):
        project = self.get_object()
        if project.owner_id != request.user.id:
            return Response({"detail": "Только владелец может архивировать"}, status=403)
        if not project.is_archived:
            project.is_archived = True
            project.archived_at = timezone.now()
            project.save(update_fields=["is_archived", "archived_at", "updated_at"])
        return Response(ProjectSerializer(project, context={"request": request}).data)

    @action(detail=True, methods=["post"], url_path="unarchive")
    def unarchive(self, request, pk=None):
        project = self.get_object()
        if project.owner_id != request.user.id:
            return Response({"detail": "Только владелец может восстанавливать"}, status=403)
        if project.is_archived:
            project.is_archived = False
            project.archived_at = None
            project.save(update_fields=["is_archived", "archived_at", "updated_at"])
        return Response(ProjectSerializer(project, context={"request": request}).data)

    @action(detail=True, methods=["post"], url_path="move-to-team")
    def move_to_team(self, request, pk=None):
        """Owner can move a project into one of their teams (or detach from team if null)."""
        from apps.teams.models import Team

        project = self.get_object()
        if project.owner_id != request.user.id:
            return Response({"detail": "Только владелец может менять команду"}, status=403)

        team_id = request.data.get("team")
        if team_id in (None, "", 0, "0"):
            project.team = None
            project.save(update_fields=["team", "updated_at"])
            return Response(ProjectSerializer(project, context={"request": request}).data)

        # Confirm the user is part of the destination team.
        team = Team.objects.filter(
            Q(pk=team_id) & (Q(owner=request.user) | Q(members__user=request.user))
        ).distinct().first()
        if not team:
            return Response({"detail": "Команда не найдена или нет доступа"}, status=404)

        project.team = team
        project.save(update_fields=["team", "updated_at"])
        return Response(ProjectSerializer(project, context={"request": request}).data)
