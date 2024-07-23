from typing import cast

from django.db.models.query import QuerySet
from rest_framework import serializers
from rest_framework.serializers import ReturnDict

from .github import Github, register_social_user
from .models import (
    AssuranceCase,
    CaseItem,
    Comment,
    Context,
    EAPGroup,
    EAPUser,
    Evidence,
    GitHubRepository,
    PropertyClaim,
    Strategy,
    TopLevelNormativeGoal,
)


class GithubSocialAuthSerializer(serializers.Serializer):
    """Handles serialization of GitHub related data"""

    auth_token = serializers.CharField()

    def validate_auth_token(self, auth_token):
        github_username, email, access_token = Github.validate(auth_token)
        try:
            email = email["email"]
            provider = "github"
        except Exception:
            msg = "The token is invalid or expired. Please login again."
            raise Exception from serializers.ValidationError(msg)
        user_info = register_social_user(provider, email, github_username)
        user_info["access_token"] = access_token
        return user_info


class GitHubRepositorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GitHubRepository
        fields = ("id", "name", "url", "description", "created_date", "owner")


class EAPUserSerializer(serializers.ModelSerializer):
    all_groups = serializers.PrimaryKeyRelatedField(
        many=True, read_only=True, required=False
    )
    owned_groups = serializers.PrimaryKeyRelatedField(
        many=True, read_only=True, required=False
    )
    github_repositories = GitHubRepositorySerializer(many=True, read_only=True)

    class Meta:
        model = EAPUser
        fields = (
            "id",
            "username",
            "email",
            "last_login",
            "date_joined",
            "is_staff",
            "all_groups",
            "owned_groups",
            "github_repositories",  # Add this line to include GitHub repositories
        )


class EAPGroupSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(
        source="member", many=True, queryset=EAPUser.objects.all()
    )
    owner_id = serializers.PrimaryKeyRelatedField(
        source="owner", queryset=EAPUser.objects.all()
    )
    viewable_cases = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    editable_cases = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = EAPGroup
        fields = (
            "id",
            "name",
            "owner_id",
            "members",
            "viewable_cases",
            "editable_cases",
        )


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    def get_author(self, obj):
        return obj.author.username

    class Meta:
        model = Comment
        fields = (
            "id",
            "author",
            "assurance_case",
            "content",
            "created_at",
        )


class AssuranceCaseSerializer(serializers.ModelSerializer):
    goals = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    type = serializers.CharField(default="AssuranceCase", read_only=True)
    color_profile = serializers.CharField(default="default")

    class Meta:
        model = AssuranceCase
        fields = (
            "id",
            "type",
            "name",
            "description",
            "created_date",
            "lock_uuid",
            "goals",
            "owner",
            "edit_groups",
            "view_groups",
            "color_profile",
            "comments",  # Add this line to include comments
        )


class SandboxSerializer(serializers.ModelSerializer):

    contexts = serializers.SerializerMethodField()
    evidence = serializers.SerializerMethodField()
    property_claims = serializers.SerializerMethodField()
    strategies = serializers.SerializerMethodField()

    class Meta:
        model = AssuranceCase
        fields = ["contexts", "evidence", "property_claims", "strategies"]

    def get_contexts(self, assurance_case: AssuranceCase) -> ReturnDict:
        sandbox_contexts: QuerySet = assurance_case.contexts.filter(in_sandbox=True)  # type: ignore[attr-defined]
        context_serializer = ContextSerializer(sandbox_contexts, many=True)
        return cast(ReturnDict, context_serializer.data)

    def get_evidence(self, assurance_case: AssuranceCase) -> ReturnDict:
        sandbox_evidence: QuerySet = assurance_case.evidence.filter(in_sandbox=True)  # type: ignore[attr-defined]
        evidence_serializer = EvidenceSerializer(sandbox_evidence, many=True)
        return cast(ReturnDict, evidence_serializer.data)

    def get_property_claims(self, assurance_case: AssuranceCase) -> ReturnDict:
        sandbox_property_claims: QuerySet = assurance_case.property_claims.filter(in_sandbox=True)  # type: ignore[attr-defined]
        property_claim_serializer = PropertyClaimSerializer(
            sandbox_property_claims, many=True
        )
        return cast(ReturnDict, property_claim_serializer.data)

    def get_strategies(self, assurance_case: AssuranceCase) -> ReturnDict:
        sandbox_strategies: QuerySet = assurance_case.strategies.filter(in_sandbox=True)  # type: ignore[attr-defined]
        strategy_serializer = StrategySerializer(sandbox_strategies, many=True)
        return cast(ReturnDict, strategy_serializer.data)


class TopLevelNormativeGoalSerializer(serializers.ModelSerializer):
    assurance_case_id = serializers.PrimaryKeyRelatedField(
        source="assurance_case", queryset=AssuranceCase.objects.all()
    )
    context = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    property_claims = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    strategies = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    type = serializers.CharField(default="TopLevelNormativeGoal", read_only=True)

    class Meta:
        model = TopLevelNormativeGoal
        fields = (
            "id",
            "type",
            "name",
            "short_description",
            "long_description",
            "keywords",
            "assurance_case_id",
            "context",
            "property_claims",
            "strategies",
        )

        extra_kwargs = {"name": {"allow_null": True, "required": False}}

    def create(self, validated_data: dict) -> TopLevelNormativeGoal:
        goal: TopLevelNormativeGoal = TopLevelNormativeGoal(**validated_data)

        assurance_case_id: int = validated_data["assurance_case"].pk
        candidate_index: int = (
            TopLevelNormativeGoal.objects.filter(
                assurance_case_id=assurance_case_id
            ).count()
            + 1
        )

        goal.name = get_unique_name(candidate_index, "G", TopLevelNormativeGoal)
        goal.save()

        return goal


class ContextSerializer(serializers.ModelSerializer):
    goal_id = serializers.PrimaryKeyRelatedField(
        source="goal", queryset=TopLevelNormativeGoal.objects.all()
    )
    type = serializers.CharField(default="Context", read_only=True)

    class Meta:
        model = Context
        fields = (
            "id",
            "type",
            "name",
            "short_description",
            "long_description",
            "created_date",
            "goal_id",
            "in_sandbox",
        )

        extra_kwargs = {"name": {"allow_null": True, "required": False}}


class PropertyClaimSerializer(serializers.ModelSerializer):
    goal_id = serializers.PrimaryKeyRelatedField(
        source="goal",
        queryset=TopLevelNormativeGoal.objects.all(),
        required=False,
        allow_null=True,
    )
    property_claim_id = serializers.PrimaryKeyRelatedField(
        source="property_claim",
        queryset=PropertyClaim.objects.all(),
        required=False,
        allow_null=True,
    )
    strategy_id = serializers.PrimaryKeyRelatedField(
        source="strategy",
        queryset=Strategy.objects.all(),
        required=False,
        allow_null=True,
    )

    level = serializers.IntegerField(read_only=True)
    claim_type = serializers.CharField(default="Project claim")
    property_claims = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    # Use SerializerMethodField to handle the possibility of property_claim
    #  being None
    evidence = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    type = serializers.CharField(default="PropertyClaim", read_only=True)

    class Meta:
        model = PropertyClaim
        fields = (
            "id",
            "type",
            "name",
            "short_description",
            "long_description",
            "goal_id",
            "property_claim_id",
            "level",
            "claim_type",
            "property_claims",
            "evidence",
            "strategy_id",
            "in_sandbox",
        )

        extra_kwargs = {
            "name": {"allow_null": True, "required": False},
        }


class EvidenceSerializer(serializers.ModelSerializer):
    property_claim_id = serializers.PrimaryKeyRelatedField(
        source="property_claim",
        queryset=PropertyClaim.objects.all(),
        many=True,
    )
    type = serializers.CharField(default="Evidence", read_only=True)

    class Meta:
        model = Evidence
        fields = (
            "id",
            "type",
            "name",
            "short_description",
            "long_description",
            "URL",
            "property_claim_id",
            "in_sandbox",
        )

        extra_kwargs = {"name": {"allow_null": True, "required": False}}


class StrategySerializer(serializers.ModelSerializer):
    goal_id = serializers.PrimaryKeyRelatedField(
        source="goal",
        queryset=TopLevelNormativeGoal.objects.all(),
        required=False,
    )

    type = serializers.CharField(default="Strategy", read_only=True)
    property_claims = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Strategy
        fields = (
            "id",
            "type",
            "name",
            "short_description",
            "long_description",
            "goal_id",
            "property_claims",
            "in_sandbox",
        )

        extra_kwargs = {"name": {"allow_null": True, "required": False}}


def get_unique_name(
    candidate_index: int, name_prefix: str, model_class: type[CaseItem]
) -> str:
    while (
        model_class.objects.filter(name=f"{name_prefix}{candidate_index}").count() != 0
    ):
        candidate_index += 1

    return f"{name_prefix}{candidate_index}"
