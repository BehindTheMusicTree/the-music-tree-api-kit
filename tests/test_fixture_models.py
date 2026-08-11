import pytest
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError

from tests.fixture_app.models import FixtureCategory, FixtureItem


@pytest.mark.django_db
def test_private_unique_resource_save_and_name_transform():
    user = get_user_model().objects.create(username="fixture-user")

    category = FixtureCategory.objects.create(user=user, _name="genre")

    assert category.uuid is not None
    assert category.created_on is not None
    assert category.updated_on is None

    fetched = FixtureCategory.objects.get(name="genre")
    assert fetched.pk == category.pk

    fetched._name = "genre-renamed"
    fetched.save()
    fetched.refresh_from_db()
    assert fetched.updated_on is not None


@pytest.mark.django_db
def test_private_unique_resource_unique_constraint_per_user():
    user = get_user_model().objects.create(username="fixture-user")
    FixtureCategory.objects.create(user=user, _name="genre")

    with pytest.raises(IntegrityError):
        FixtureCategory.objects.create(user=user, _name="genre")


@pytest.mark.django_db
def test_foreign_key_family_relations():
    user = get_user_model().objects.create(username="fixture-user")
    category = FixtureCategory.objects.create(user=user, _name="genre")
    partner = FixtureCategory.objects.create(user=user, _name="partner")

    item = FixtureItem.objects.create(user=user, _name="item", category=category, partner_category=partner)
    item.related_categories.set([category, partner])

    assert item.category_id == category.pk
    assert item.partner_category_id == partner.pk
    assert set(item.related_categories.all()) == {category, partner}
    assert item in category.items.all()
