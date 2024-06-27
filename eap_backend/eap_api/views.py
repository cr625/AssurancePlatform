from typing import Callable, Optional, cast

from django.db.models import Q
from django.db.models.query import QuerySet
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import GenericAPIView
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

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
from .serializers import (
    AssuranceCaseSerializer,
    CommentSerializer,
    ContextSerializer,
    EAPGroupSerializer,
    EAPUserSerializer,
    EvidenceSerializer,
    GitHubRepositorySerializer,
    GithubSocialAuthSerializer,
    PropertyClaimSerializer,
    StrategySerializer,
    TopLevelNormativeGoalSerializer,
)
from .view_utils import (
    TYPE_DICT,
    can_view_group,
    filter_by_case_id,
    get_allowed_cases,
    get_allowed_groups,
    get_case_id,
    get_case_permissions,
    get_json_tree,
    make_case_summary,
    make_summary,
    save_json_tree,
)


@csrf_exempt
def user_list(request) -> Optional[HttpResponse]:
    """
    List all users, or make a new user
    """
    if request.method == "GET":
        users = EAPUser.objects.all()
        serializer = EAPUserSerializer(users, many=True)
        return JsonResponse(serializer.data, safe=False)
    elif request.method == "POST":
        data = JSONParser().parse(request)
        serializer = EAPUserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)
    return None


@csrf_exempt
@api_view(["GET"])
def self_detail(request):
    """
    Retrieve, update, or delete a User by primary key
    """
    pk = request.user.id
    try:
        user = EAPUser.objects.get(pk=pk)
    except EAPUser.DoesNotExist:
        return HttpResponse(status=404)
    if request.user != user:
        return HttpResponse(status=403)
    if request.method == "GET":
        serializer = EAPUserSerializer(user)
        user_data = serializer.data
        return JsonResponse(user_data)
    return None


@csrf_exempt
@api_view(["GET", "PUT", "DELETE", "POST"])
def user_detail(request, pk=None):
    """
    Retrieve, update, or delete a User by primary key
    """
    try:
        user = EAPUser.objects.get(pk=pk)
    except EAPUser.DoesNotExist:
        return HttpResponse(status=404)
    if request.user != user:
        return HttpResponse(status=403)
    if request.method == "GET":
        serializer = EAPUserSerializer(user)
        user_data = serializer.data
        return JsonResponse(user_data)
    elif request.method == "PUT":
        data = JSONParser().parse(request)
        serializer = EAPUserSerializer(user, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)
    elif request.method == "DELETE":
        user.delete()
        return HttpResponse(status=204)
    elif request.method == "POST":
        # This block assumes you are receiving GitHub repository data to add to the user
        repo_serializer = GitHubRepositorySerializer(data=request.data)
        if repo_serializer.is_valid():
            repo_serializer.save(owner=user)
            return JsonResponse(repo_serializer.data, status=201)
        return JsonResponse(repo_serializer.errors, status=400)

    return None


@csrf_exempt
@api_view(["GET", "POST"])
def group_list(request):
    """
    List all group, or make a new group
    """
    if request.method == "GET":
        response_dict = {}
        for level in ["owner", "member"]:
            groups = get_allowed_groups(request.user, level)
            serializer = EAPGroupSerializer(groups, many=True)
            response_dict[level] = serializer.data
        return JsonResponse(response_dict, safe=False)
    elif request.method == "POST":
        data = JSONParser().parse(request)
        data["owner_id"] = request.user.id
        data["members"] = [request.user.id]
        serializer = EAPGroupSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)
    return None


@csrf_exempt
@api_view(["GET", "PUT", "DELETE"])
def group_detail(request, pk):
    """
    Retrieve, update, or delete a Group by primary key
    """
    try:
        group = EAPGroup.objects.get(pk=pk)
    except EAPGroup.DoesNotExist:
        return HttpResponse(status=404)
    if not can_view_group(group, request.user, "owner"):
        return HttpResponse(status=403)
    if request.method == "GET":
        serializer = EAPGroupSerializer(group)
        group_data = serializer.data
        return JsonResponse(group_data)
    elif request.method == "PUT":
        data = JSONParser().parse(request)
        serializer = EAPGroupSerializer(group, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)
    elif request.method == "DELETE":
        group.delete()
        return HttpResponse(status=204)
    return None


@csrf_exempt
@api_view(["GET", "POST"])
def case_list(request):
    """
    List all cases, or make a new case
    """
    if request.method == "GET":
        cases = get_allowed_cases(request.user)
        serializer = AssuranceCaseSerializer(cases, many=True)
        summaries = make_case_summary(serializer.data)
        return JsonResponse(summaries, safe=False)
    elif request.method == "POST":
        data = JSONParser().parse(request)
        data["owner"] = request.user.id
        return save_json_tree(data, "assurance_case")
    return None


# @csrf_exempt
# @api_view(["GET", "POST", "PUT", "DELETE"])
# def case_detail(request, pk):
#     """
#     Retrieve, update, or delete an AssuranceCase, by primary key
#     """
#     try:
#         case = AssuranceCase.objects.get(pk=pk)
#     except AssuranceCase.DoesNotExist:
#         return HttpResponse(status=404)
#     permissions = get_case_permissions(case, request.user)
#     if not permissions:
#         return HttpResponse(status=403)
#     if request.method == "GET":
#         serializer = AssuranceCaseSerializer(case)
#         case_data = serializer.data
#         goals = get_json_tree(case_data["goals"], "goals")
#         case_data["goals"] = goals
#         case_data["permissions"] = permissions
#         return JsonResponse(case_data)
#     elif request.method == "PUT":
#         if permissions not in ["manage", "edit"]:
#             return HttpResponse(status=403)
#         data = JSONParser().parse(request)
#         serializer = AssuranceCaseSerializer(case, data=data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return JsonResponse(serializer.data)
#         return JsonResponse(serializer.errors, status=400)
#     elif request.method == "DELETE":
#         if permissions not in ["manage", "edit"]:
#             return HttpResponse(status=403)
#         case.delete()
#         return HttpResponse(status=204)


#     return None
@csrf_exempt
@api_view(["GET", "POST", "PUT", "DELETE"])
def case_detail(request, pk):
    """
    Retrieve, update, or delete an AssuranceCase, by primary key
    """
    try:
        case = AssuranceCase.objects.get(pk=pk)
    except AssuranceCase.DoesNotExist:
        return HttpResponse(status=404)
    permissions = get_case_permissions(case, request.user)
    if not permissions:
        return HttpResponse(status=403)
    if request.method == "GET":
        serializer = AssuranceCaseSerializer(case)
        case_data = serializer.data
        goals = get_json_tree(case_data["goals"], "goals")
        case_data["goals"] = goals
        case_data["permissions"] = permissions
        return JsonResponse(case_data)
    elif request.method == "PUT":
        if permissions not in ["manage", "edit"]:
            return HttpResponse(status=403)
        data = JSONParser().parse(request)
        serializer = AssuranceCaseSerializer(case, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)
    elif request.method == "DELETE":
        if permissions not in ["manage", "edit"]:
            return HttpResponse(status=403)
        case.delete()
        return HttpResponse(status=204)

    return None


@csrf_exempt
def goal_list(request):
    """
    List all goals, or make a new goal
    """
    if request.method == "GET":
        goals = TopLevelNormativeGoal.objects.all()
        goals = filter_by_case_id(goals, request)
        serializer = TopLevelNormativeGoalSerializer(goals, many=True)
        summaries = make_summary(serializer.data)
        return JsonResponse(summaries, safe=False)
    elif request.method == "POST":

        data = JSONParser().parse(request)
        assurance_case_id = AssuranceCase.objects.get(id=data["assurance_case_id"])
        data["assurance_case"] = assurance_case_id
        serializer = TopLevelNormativeGoalSerializer(data=data)
        if serializer.is_valid():
            model_instance: TopLevelNormativeGoal = cast(
                TopLevelNormativeGoal, serializer.save()
            )
            update_identifiers(model_instance=model_instance)

            serialised_model = TopLevelNormativeGoalSerializer(model_instance)
            return JsonResponse(serialised_model.data, status=201)

        return JsonResponse(serializer.errors, status=400)
    return None


@csrf_exempt
def goal_detail(request, pk):
    """
    Retrieve, update, or delete a TopLevelNormativeGoal, by primary key
    """
    try:
        goal = TopLevelNormativeGoal.objects.get(pk=pk)
        shape = goal.shape.name
    except TopLevelNormativeGoal.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == "GET":
        serializer = TopLevelNormativeGoalSerializer(goal)
        data = serializer.data
        # replace IDs for children with full JSON objects
        for key in ["context", "property_claims"]:
            data[key] = get_json_tree(data[key], key)
        data["shape"] = shape
        return JsonResponse(data)
    elif request.method == "PUT":
        data = JSONParser().parse(request)
        serializer = TopLevelNormativeGoalSerializer(goal, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            data = serializer.data
            data["shape"] = shape
            return JsonResponse(data)
        return JsonResponse(serializer.errors, status=400)
    elif request.method == "DELETE":
        case_id: Optional[int] = get_case_id(goal)
        goal.delete()
        update_identifiers(case_id)
        return HttpResponse(status=204)
    return None


@csrf_exempt
def context_list(request):
    """
    List all contexts, or make a new context
    """
    if request.method == "GET":
        contexts = Context.objects.all()
        contexts = filter_by_case_id(contexts, request)
        serializer = ContextSerializer(contexts, many=True)
        summaries = make_summary(serializer.data)
        return JsonResponse(summaries, safe=False)
    elif request.method == "POST":
        data = JSONParser().parse(request)
        serializer = ContextSerializer(data=data)
        if serializer.is_valid():
            model_instance: Context = cast(Context, serializer.save())
            update_identifiers(model_instance=model_instance)
            summary = make_summary(model_instance)
            return JsonResponse(summary, status=201)
        return JsonResponse(serializer.errors, status=400)
    return None


@csrf_exempt
def context_detail(request, pk):
    """
    Retrieve, update, or delete a Context, by primary key
    """
    try:
        context = Context.objects.get(pk=pk)
        shape = context.shape.name
    except Context.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == "GET":
        serializer = ContextSerializer(context)
        data = serializer.data
        data["shape"] = shape
        return JsonResponse(data)
    elif request.method == "PUT":
        data = JSONParser().parse(request)
        serializer = ContextSerializer(context, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            data = serializer.data
            data["shape"] = shape
            return JsonResponse(data)
        return JsonResponse(serializer.errors, status=400)
    elif request.method == "DELETE":
        case_id: Optional[int] = get_case_id(context)
        context.delete()
        update_identifiers(case_id=case_id)
        return HttpResponse(status=204)
    return None


@csrf_exempt
def property_claim_list(request):
    """
    List all claims, or make a new claim
    """
    if request.method == "GET":
        claims = PropertyClaim.objects.all()
        claims = filter_by_case_id(claims, request)
        serializer = PropertyClaimSerializer(claims, many=True)
        summaries = make_summary(serializer.data)
        return JsonResponse(summaries, safe=False)
    elif request.method == "POST":
        data = JSONParser().parse(request)
        serializer = PropertyClaimSerializer(data=data)
        if serializer.is_valid():
            model_instance: PropertyClaim = cast(PropertyClaim, serializer.save())
            update_identifiers(model_instance=model_instance)

            serialised_model = PropertyClaimSerializer(model_instance)
            return JsonResponse(serialised_model.data, status=201)
        return JsonResponse(serializer.errors, status=400)
    return None


@csrf_exempt
def property_claim_detail(request, pk):
    """
    Retrieve, update, or delete a PropertyClaim, by primary key
    """
    try:
        claim = PropertyClaim.objects.get(pk=pk)
        shape = claim.shape.name
    except PropertyClaim.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == "GET":
        serializer = PropertyClaimSerializer(claim)
        data = serializer.data
        data["shape"] = shape
        return JsonResponse(data)
    elif request.method == "PUT":
        data = JSONParser().parse(request)
        serializer = PropertyClaimSerializer(claim, data=data, partial=True)
        if serializer.is_valid():
            model_instance: PropertyClaim = cast(PropertyClaim, serializer.save())
            update_identifiers(model_instance=model_instance)

            data: dict = cast(
                dict,
                PropertyClaimSerializer(model_instance).data,
            )
            data["shape"] = shape

            return JsonResponse(data)
        return JsonResponse(serializer.errors, status=400)
    elif request.method == "DELETE":
        case_id: Optional[int] = get_case_id(claim)
        claim.delete()
        update_identifiers(case_id=case_id)
        return HttpResponse(status=204)
    return None


@csrf_exempt
def evidence_list(request):
    """
    List all evidences, or make a new evidence
    """
    if request.method == "GET":
        evidences = Evidence.objects.all()
        evidences = filter_by_case_id(evidences, request)
        serializer = EvidenceSerializer(evidences, many=True)
        summaries = make_summary(serializer.data)
        return JsonResponse(summaries, safe=False)
    elif request.method == "POST":
        data = JSONParser().parse(request)
        serializer = EvidenceSerializer(data=data)
        if serializer.is_valid():
            model_instance: Evidence = cast(Evidence, serializer.save())
            update_identifiers(model_instance=model_instance)
            summary = make_summary(model_instance)
            return JsonResponse(summary, status=201)
        return JsonResponse(serializer.errors, status=400)
    return None


@csrf_exempt
def evidence_detail(request, pk):
    """
    Retrieve, update, or delete Evidence, by primary key
    """
    try:
        evidence = Evidence.objects.get(pk=pk)
        shape = evidence.shape.name
    except Evidence.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == "GET":
        serializer = EvidenceSerializer(evidence)
        data = serializer.data
        data["shape"] = shape
        return JsonResponse(data)
    elif request.method == "PUT":
        data = JSONParser().parse(request)
        serializer = EvidenceSerializer(evidence, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            data = serializer.data
            data["shape"] = shape
            return JsonResponse(data)
        return JsonResponse(serializer.errors, status=400)
    elif request.method == "DELETE":
        case_id: Optional[int] = get_case_id(evidence)
        evidence.delete()
        update_identifiers(case_id=case_id)
        return HttpResponse(status=204)
    return None


@csrf_exempt
def parents(request, item_type, pk):
    """Return all the parents of an item."""
    if request.method != "GET":
        return HttpResponse(status=404)
    item = TYPE_DICT[item_type]["model"].objects.get(pk=pk)
    parent_types = TYPE_DICT[item_type]["parent_types"]
    parents_data = []
    for parent_type, many in parent_types:
        serializer_class = TYPE_DICT[parent_type]["serializer"]
        parent = getattr(item, parent_type)
        if parent is None:
            continue
        parents_data += serializer_class(parent, many=many).data
    return JsonResponse(parents_data, safe=False)


@csrf_exempt
def strategies_list(request):
    """
    List all strategies, or make a new strategy
    """
    if request.method == "GET":
        strategies = Strategy.objects.all()
        strategies = filter_by_case_id(strategies, request)
        serializer = StrategySerializer(strategies, many=True)
        summaries = make_summary(serializer.data)
        return JsonResponse(summaries, safe=False)
    elif request.method == "POST":
        data = JSONParser().parse(request)
        serializer = StrategySerializer(data=data)
        if serializer.is_valid():
            model_instance: Strategy = cast(Strategy, serializer.save())
            update_identifiers(model_instance=model_instance)

            serialised_model = StrategySerializer(model_instance)
            return JsonResponse(serialised_model.data, status=201)
        return JsonResponse(serializer.errors, status=400)
    return None


@csrf_exempt
def strategy_detail(request, pk):
    try:
        strategy = Strategy.objects.get(pk=pk)
    except Strategy.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == "GET":
        serializer = StrategySerializer(strategy)
        return JsonResponse(serializer.data)

    elif request.method == "PUT":
        data = JSONParser().parse(request)
        serializer = StrategySerializer(strategy, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            summary = make_summary(serializer.data)
            return JsonResponse(summary)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == "DELETE":
        case_id: Optional[int] = get_case_id(strategy)
        strategy.delete()
        update_identifiers(case_id=case_id)
        return HttpResponse(status=204)
    return None


@permission_classes((AllowAny,))
class GithubSocialAuthView(GenericAPIView):
    serializer_class = GithubSocialAuthSerializer

    def post(self, request):
        """
        POST with "auth_token"
        Send an access token from GitHub to get user information
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = (serializer.validated_data)["auth_token"]
        return Response(data, status=status.HTTP_200_OK)


class CommentEdit(generics.UpdateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


@api_view(["GET", "POST"])
def github_repository_list(request):
    """
    GET: List all GitHub repositories for a user.
    POST: Add a new GitHub repository to a user.
    """
    if request.method == "GET":
        repositories = GitHubRepository.objects.filter(owner=request.user)
        serializer = GitHubRepositorySerializer(repositories, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        # Assume the POST data includes fields for creating a GitHubRepository
        request.data["owner"] = request.user.id
        serializer = GitHubRepositorySerializer(data=request.data)
        if serializer.is_valid():
            # Set the owner to the current user before saving
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "POST"])
def comment_list(request, assurance_case_id):
    """
    List all comments for an assurance case, or create a new comment.
    """
    permissions = get_case_permissions(assurance_case_id, request.user)
    if not permissions:
        return HttpResponse(status=403)

    if request.method == "GET":
        comments = Comment.objects.filter(assurance_case_id=assurance_case_id)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        data = request.data.copy()
        data["assurance_case_id"] = (
            assurance_case_id  # Ensure assurance_case_id is set in the data
        )
        serializer = CommentSerializer(data=data)
        if serializer.is_valid():
            # Ensure the author is set to the current user
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "DELETE"])
def comment_detail(request, pk):
    """
    Retrieve, update or delete a specific comment.
    """
    try:
        comment = Comment.objects.get(id=pk)
    except Comment.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == "GET":
        serializer = CommentSerializer(comment)
        return Response(serializer.data)

    elif request.method == "PUT":
        serializer = CommentSerializer(comment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        comment.delete()
        return HttpResponse(status=204)

    return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def reply_to_comment(request, comment_id):
    """
    Reply to an existing comment.
    """
    try:
        parent_comment = Comment.objects.get(pk=comment_id)
        assurance_case_id = parent_comment.assurance_case_id
    except Comment.DoesNotExist:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)

    permissions = get_case_permissions(assurance_case_id, request.user)
    if not permissions:
        return HttpResponse(status=403)

    if request.method == "POST":
        data = JSONParser().parse(request)
        data["parent"] = comment_id
        data["author"] = request.user.id  # Ensure the author is set to the current user
        data["assurance_case"] = parent_comment.assurance_case_id
        serializer = CommentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def update_identifiers(
    case_id: Optional[int] = None, model_instance: Optional[CaseItem] = None
):

    error_message: str = "Assurance Case ID not provided."
    if case_id is None and model_instance is not None:
        case_id = get_case_id(model_instance)

    if case_id is None:
        raise ValueError(error_message)

    if TopLevelNormativeGoal.objects.filter(assurance_case_id=case_id).exists():

        current_case_goal: TopLevelNormativeGoal = TopLevelNormativeGoal.objects.get(
            assurance_case_id=case_id
        )
        goal_id: int = current_case_goal.pk

        update_sequential_identifiers(
            TopLevelNormativeGoal.objects.filter(id=goal_id).order_by("id"),
            "G",
        )

        update_sequential_identifiers(
            Context.objects.filter(goal_id=goal_id).order_by("id"), "C"
        )

        current_case_strategies: QuerySet = Strategy.objects.filter(
            goal_id=goal_id
        ).order_by("id")
        update_sequential_identifiers(current_case_strategies, "S")

        top_level_claim_ids, child_claim_ids = get_case_property_claims(
            current_case_goal, current_case_strategies
        )

        update_sequential_identifiers(
            Evidence.objects.filter(
                property_claim__id__in=top_level_claim_ids + child_claim_ids
            ).order_by("id"),
            "E",
        )

        parent_property_claims: QuerySet = PropertyClaim.objects.filter(
            pk__in=top_level_claim_ids
        ).order_by("id")

        update_sequential_identifiers(parent_property_claims, "P")

        for _, property_claim in enumerate(parent_property_claims):
            traverse_child_property_claims(
                lambda index, child, parent: update_item_name(
                    child, f"{parent.name}.", index + 1
                ),
                property_claim.pk,
            )

        if model_instance is not None:
            model_instance.refresh_from_db()


def get_case_property_claims(
    goal: TopLevelNormativeGoal, strategies: QuerySet
) -> tuple:
    strategy_ids: list[int] = [strategy.pk for strategy in strategies]

    top_level_claim_ids: list[int] = [
        claim.pk
        for claim in PropertyClaim.objects.filter(
            Q(goal_id=goal.pk) | Q(strategy__id__in=strategy_ids)
        ).order_by("id")
    ]

    child_claim_ids: list[int] = []
    for parent_claim_id in top_level_claim_ids:
        traverse_child_property_claims(
            lambda _, child, parent: child_claim_ids.append(child.pk),  # noqa: ARG005
            parent_claim_id,
        )

    return top_level_claim_ids, sorted(child_claim_ids)


def traverse_child_property_claims(
    on_child_claim: Callable[[int, PropertyClaim, PropertyClaim], None],
    parent_claim_id: int,
):

    child_property_claims = PropertyClaim.objects.filter(
        property_claim_id=parent_claim_id
    ).order_by("id")

    if len(child_property_claims) == 0:
        return
    else:
        for index, child_property_claim in enumerate(child_property_claims):
            on_child_claim(
                index,
                child_property_claim,
                PropertyClaim.objects.get(pk=parent_claim_id),
            )
            traverse_child_property_claims(on_child_claim, child_property_claim.pk)


def update_item_name(case_item: CaseItem, prefix: str, number: int) -> None:
    case_item.name = f"{prefix}{number}"
    case_item.save()


def update_sequential_identifiers(query_set: QuerySet, prefix: str):
    for model_index, model in enumerate(query_set):
        update_item_name(model, prefix, model_index + 1)
