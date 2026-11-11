from django.db import models

from .Fields import Fields


class CommonsImage(models.Model):
    """Wikimedia Commons image whose attribution (author, license linked to the Commons page) must be shown with it.

    Concrete models must add ``commons_image_complete_constraint("<app>_<model>_image_complete")`` to their own
    ``Meta.constraints``: a subclass that declares its own ``Meta`` does not inherit this one, so the constraint cannot
    live here.
    """

    image_url = models.URLField(max_length=2048, null=True, blank=True)
    image_page_url = models.URLField(max_length=2048, null=True, blank=True)
    image_author = models.TextField(null=True, blank=True)
    image_license = models.TextField(null=True, blank=True)
    image_license_url = models.URLField(max_length=2048, null=True, blank=True)

    class Meta:
        abstract = True


def commons_image_complete_constraint(name: str) -> models.CheckConstraint:
    """The url, page url and license are set together; otherwise all five columns are null."""
    return models.CheckConstraint(
        condition=models.Q(
            **{f"{Fields.IMAGE_URL}__isnull": False},
            **{f"{Fields.IMAGE_PAGE_URL}__isnull": False},
            **{f"{Fields.IMAGE_LICENSE}__isnull": False},
        )
        | models.Q(**{f"{field}__isnull": True for field in Fields.ALL}),
        name=name,
    )
