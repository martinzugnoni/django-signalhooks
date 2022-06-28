from django.core.serializers import register_serializer
from django.core.management import call_command
from django.db import connection
from django.test import TestCase
from signalhooks.hooks import SNSSignalHook
from tests.models import Parent, Child, AnotherChild
from expected_responses import *
import base64
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
        self.c1.another_children = self.ac1
        self.c2 = ChildFactory(name="Child2", desc="Description for child2",)

        self.parent = ParentFactory(
            name="New Parent", child=self.c1, main_child=self.c2
        )
        self.parent.another_children.add(self.ac1)
        self.parent.another_children.add(self.ac2)

    def test_serializer_with_no_nested_fields_no_depth(self):
        sns_hook = SNSSignalHook(sns_topic_arn="test_topic", serializer="json.nested")
        result = sns_hook.get_sns_msg_attributes(instance=self.parent, created=True)
        print(result)
        self.assertEqual(
            base64.b64decode(result["Instance"]["StringValue"]).decode("utf-8"),
            NO_NESTED_FIELDS_DEFAULT_DEPTH,
        )

    def test_serializer_with_nested_fields_no_depth(self):
        sns_hook = SNSSignalHook(
            sns_topic_arn="test_topic",
            serializer="json.nested",
            nested_fields=["child"],
        )
        result = sns_hook.get_sns_msg_attributes(instance=self.parent, created=True)
        print(result)
        self.assertEqual(
            base64.b64decode(result["Instance"]["StringValue"]).decode("utf-8"),
            NESTED_FIELDS_DEFAULT_DEPTH,
        )

    def test_serializer_with_nested_fields_depth_1(self):
        sns_hook = SNSSignalHook(
            sns_topic_arn="test_topic",
            serializer="json.nested",
            nested_fields=["child"],
            max_depth=1,
        )
        result = sns_hook.get_sns_msg_attributes(instance=self.parent, created=True)
        self.assertEqual(
            base64.b64decode(result["Instance"]["StringValue"]).decode("utf-8"),
            NESTED_FIELDS_DEPTH_1,
        )

    def test_serializer_with_nested_fields_depth_2(self):
        sns_hook = SNSSignalHook(
            sns_topic_arn="test_topic",
            serializer="json.nested",
            nested_fields=["child", "another_children"],
            max_depth=2,
        )
        result = sns_hook.get_sns_msg_attributes(instance=self.parent, created=True)
        self.assertEqual(
            base64.b64decode(result["Instance"]["StringValue"]).decode("utf-8"),
            NESTED_FIELDS_DEPTH_2,
        )

    def test_serializer_with_array_nested_fields_depth(self):
        sns_hook = SNSSignalHook(
            sns_topic_arn="test_topic",
            serializer="json.nested",
            nested_fields=["another_children"],
        )
        result = sns_hook.get_sns_msg_attributes(instance=self.parent, created=True)
        self.assertEqual(
            base64.b64decode(result["Instance"]["StringValue"]).decode("utf-8"),
            ARRAY_NESTED_FIELDS_DEPTH_1,
        )


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
