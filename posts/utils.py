from django.db.models import BooleanField, Count, Exists, OuterRef, Value

from .models import Like


def annotate_posts(queryset, viewer):
    """
    Attach like_count / comment_count and a `liked` flag for the current viewer
    to a Post queryset - avoids N+1 queries in the feed.
    """
    queryset = queryset.select_related("author", "author__profile").annotate(
        like_count=Count("likes", distinct=True),
        comment_count=Count("comments", distinct=True),
    )
    if viewer.is_authenticated:
        queryset = queryset.annotate(liked=Exists(Like.objects.filter(post=OuterRef("pk"), user=viewer)))
    else:
        queryset = queryset.annotate(liked=Value(False, output_field=BooleanField()))
    return queryset.order_by("-created")
