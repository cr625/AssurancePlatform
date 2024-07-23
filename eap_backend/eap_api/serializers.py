import warnings
from typing import Any, Optional, cast

from django.db.models.query import QuerySet
from rest_framework import serializers
from rest_framework.serializers import ReturnDict

from . import models
from .github import Github, register_social_user
from .model_utils import get_case_property_claims
from .models import (
    AssuranceCase,
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

        assurance_case_id: int = validated_data["assurance_case"].pk

        validated_data["name"] = _get_unique_name(
            TopLevelNormativeGoal.objects.filter(assurance_case_id=assurance_case_id),
            "G",
        )

        return super().create(validated_data)


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

    def create(self, validated_data: dict):
        validated_data["name"] = _get_unique_name(
            Context.objects.filter(goal_id=validated_data["goal"].pk), "C"
        )

        return super().create(validated_data)


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

    def create(self, validated_data: dict) -> Evidence:

        case_id: int | None = get_case_id(validated_data["property_claim"][0])
        if case_id is None:
            error_message: str = "Cannot find assurance case for Evidence"
            raise ValueError(error_message)

        current_case_goal: TopLevelNormativeGoal = TopLevelNormativeGoal.objects.get(
            assurance_case_id=case_id
        )

        current_case_strategies: QuerySet = Strategy.objects.filter(
            goal_id=current_case_goal.pk
        )

        (
            top_level_claim_ids,
            child_claim_ids,
        ) = get_case_property_claims(current_case_goal, current_case_strategies)

        validated_data["name"] = _get_unique_name(
            Evidence.objects.filter(
                property_claim__id__in=top_level_claim_ids + child_claim_ids
            ),
            "E",
        )

        return super().create(validated_data)


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

    def create(self, validated_data: dict) -> Strategy:

        validated_data["name"] = _get_unique_name(
            Strategy.objects.filter(goal_id=validated_data["goal"].pk), "S"
        )
        return super().create(validated_data)


def _get_unique_name(base_query_set: QuerySet, name_prefix: str) -> str:

    candidate_index: int = base_query_set.count() + 1
    while base_query_set.filter(name=f"{name_prefix}{candidate_index}").count() != 0:
        candidate_index += 1

    return f"{name_prefix}{candidate_index}"


def get_type_dictionary() -> dict[str, Any]:
    type_dictionary: dict[str, Any] = {
        "assurance_case": {
            "serializer": AssuranceCaseSerializer,
            "model": AssuranceCase,
            "children": ["goals"],
            "fields": (
                "name",
                "description",
                "lock_uuid",
                "owner",
                "color_profile",
            ),
        },
        "goal": {
            "serializer": TopLevelNormativeGoalSerializer,
            "model": TopLevelNormativeGoal,
            "children": ["context", "property_claims", "strategies"],
            "fields": (
                "name",
                "short_description",
                "long_description",
                "keywords",
            ),
            "parent_types": [("assurance_case", False)],
        },
        "context": {
            "serializer": ContextSerializer,
            "model": Context,
            "children": [],
            "fields": ("name", "short_description", "long_description"),
            "parent_types": [("goal", False)],
        },
        "property_claim": {
            "serializer": PropertyClaimSerializer,
            "model": PropertyClaim,
            "children": ["property_claims", "evidence"],
            "fields": ("name", "short_description", "long_description"),
            "parent_types": [
                ("goal", False),
                ("property_claim", False),
                ("strategy", False),
            ],
        },
        "strategy": {
            "serializer": StrategySerializer,
            "model": Strategy,
            "children": ["property_claims"],
            "fields": ("name", "short_description", "long_description"),
            "parent_types": [
                ("goal", False),
            ],
        },
        "evidence": {
            "serializer": EvidenceSerializer,
            "model": Evidence,
            "children": [],
            "fields": ("name", "short_description", "long_description", "URL"),
            "parent_types": [("property_claim", True)],
        },
    }

    # Pluralising the name of the type should be irrelevant.
    for k, v in tuple(type_dictionary.items()):
        type_dictionary[k + "s" if not k.endswith("y") else k[:-1] + "ies"] = v

    return type_dictionary


TYPE_DICT = get_type_dictionary()


def get_case_id(item) -> Optional[int]:
    """Return the id of the case in which this item is. Works for all item types."""
    # In some cases, when there's a ManyToManyField, instead of the parent item, we get
    # an iterable that can potentially list all the parents. In that case, just pick the
    # first.
    if hasattr(item, "first"):
        item = item.first()

    if isinstance(item, models.AssuranceCase):
        return item.id
    for _k, v in TYPE_DICT.items():
        if isinstance(item, v["model"]):
            for parent_type, _ in v["parent_types"]:
                parent = getattr(item, parent_type)
                if parent is not None:
                    return get_case_id(parent)
    # TODO This should probably be an error raise rather than a warning, but currently
    # there are dead items in the database without parents which hit this branch.
    msg = f"Can't figure out the case ID of {item}."
    warnings.warn(msg)
    return None
