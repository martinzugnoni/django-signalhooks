from django.core.serializers import register_serializer
from django.core.serializers import serialize
from django.core.management import call_command
from django.db import connection
from django.test import TestCase
from signalhooks.models import Parent, Child, AnotherChild
from expected_responses import *
import pytest
import factory


@pytest.mark.django_db
class TestSetup(TestCase):
    def setUp(self):
        super().setUp()
        connection.disable_constraint_checking()

        register_serializer("json.nested", "signalhooks.serializer.nested")
        self.ac1 = AnotherChildFactory(name="Another Child 1")
        self.ac2 = AnotherChildFactory(name="Another Child 2")
        self.c1 = ChildFactory.create(name="Child", desc="Description for child1")
        self.c1.anotherChildren = self.ac1
        self.c2 = ChildFactory(name="Child2", desc="Description for child2",)

        self.parent = ParentFactory(name="New Parent", child=self.c1, mainChild=self.c2)
        self.parent.anotherChildren.add(self.ac1)
        self.parent.anotherChildren.add(self.ac2)

    def test_serializer_with_no_nested_fields_no_depth(self):
        result = serialize("json.nested", [self.parent])
        print(result)
        self.assertEqual(result, NO_NESTED_FIELDS_DEFAULT_DEPTH)

    def test_serializer_with_nested_fields_no_depth(self):
        result = serialize("json.nested", [self.parent], nested_fields=["child"])
        print(result)
        self.assertEqual(result, NESTED_FIELDS_DEFAULT_DEPTH)

    def test_serializer_with_nested_fields_depth_1(self):
        result = serialize(
            "json.nested", [self.parent], nested_fields=["child"], max_depth=1
        )
        print(result)
        self.assertEqual(result, NESTED_FIELDS_DEPTH_1)

    def test_serializer_with_nested_fields_depth_2(self):
        result = serialize(
            "json.nested",
            [self.parent],
            nested_fields=["child", "anotherChildren"],
            max_depth=2,
        )
        print(result)
        self.assertEqual(result, NESTED_FIELDS_DEPTH_2)

    def test_serializer_with_array_nested_fields_depth(self):
        result = serialize(
            "json.nested", [self.parent], nested_fields=["anotherChildren"]
        )
        print(result)
        self.assertEqual(result, ARRAY_NESTED_FIELDS_DEPTH_1)


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


@pytest.fixture(autouse=True)
@pytest.mark.django_db()
def fixture():
    call_command("makemigrations", "tests")
    connection.disable_constraint_checking()
    call_command("migrate", "tests")
