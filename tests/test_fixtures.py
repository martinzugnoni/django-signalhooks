from django.db import connection
from django.core.management import call_command
from tests.models import Parent, Child, AnotherChild
import factory
import pytest


@pytest.fixture(autouse=True)
@pytest.mark.django_db()
def fixture():
    call_command("makemigrations", "tests")
    connection.disable_constraint_checking()
    call_command("migrate", "tests")


class AnotherChildFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AnotherChild

    name = "anotherChild"


class ChildFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Child

    name = "default name"
    desc = "default desc"


class ParentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Parent

    name = "Parent Name"
