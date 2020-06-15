import os
import json
import base64

from django.test import TestCase
from django.db.models.signals import post_save
from django.db import models

import moto
import boto3
import pytest
import responses

from signalhooks.hooks import SNSSignalHook, HTTPSignalHook


class FakeModel(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        app_label = "tests"


class BaseHooksTestCase(TestCase):
    pass


class SNSSignalHookTestCase(BaseHooksTestCase):
    def setUp(self):
        """
        Overwrite AWS auth env vars to avoid real requests.
        """
        os.environ["AWS_ACCESS_KEY_ID"] = "testing"
        os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
        os.environ["AWS_SECURITY_TOKEN"] = "testing"
        os.environ["AWS_SESSION_TOKEN"] = "testing"

    @moto.mock_sns
    @moto.mock_sqs
    @pytest.mark.django_db
    def test_sns_signal_hook(self):
        """
        Should send a SNS Notification with the serialized Model instance.
        """
        sns_client = boto3.client("sns", region_name="us-east-1")
        topic = sns_client.create_topic(Name="testing-topic")
        topic_arn = topic["TopicArn"]

        # add SQS subscriber to be able to read a message
        # normally you will use webhook (http, https) subscribers to
        # notify other services
        sqs_client = boto3.client("sqs", region_name="us-east-1")
        queue_url = sqs_client.create_queue(QueueName="test-queue")["QueueUrl"]
        queue_arn = sqs_client.get_queue_attributes(QueueUrl=queue_url)["Attributes"][
            "QueueArn"
        ]
        sns_client.subscribe(TopicArn=topic_arn, Protocol="sqs", Endpoint=queue_arn)

        hook = SNSSignalHook(sns_topic_arn=topic_arn)
        post_save.connect(hook, sender=FakeModel)

        instance = FakeModel()
        instance.name = "Neapolitan"
        post_save.send(instance=instance, sender=FakeModel, created=True)

        msg = sqs_client.receive_message(QueueUrl=queue_url)
        body = json.loads(msg["Messages"][0]["Body"])

        self.assertEqual(body["Message"], "Django Signal triggered")
        self.assertEqual(
            body["MessageAttributes"],
            {
                "Event": {"Type": "String", "Value": "tests.fakemodel:created"},
                "InstanceId": {"Type": "String", "Value": "None"},
                "Instance": {
                    "Type": "String",
                    "Value": "eyJtb2RlbCI6ICJ0ZXN0cy5mYWtlbW9kZWwiLCAicGsiOiBudWxsLCAiZmllbGRzIjogeyJuYW1lIjogIk5lYXBvbGl0YW4ifX0=",
                },
            },
        )

        json_instance = json.loads(
            base64.b64decode(body["MessageAttributes"]["Instance"]["Value"])
        )
        self.assertEqual(
            json_instance,
            {"model": "tests.fakemodel", "pk": None, "fields": {"name": "Neapolitan"}},
        )


class HTTPSignalHookTestCase(BaseHooksTestCase):
    @responses.activate
    @pytest.mark.django_db
    def test_http_signal_hook(self):
        """
        Should make a HTTP request to subscribed hook URL.
        """
        hook_url = "https://your-other-service.io/api/1/hook"
        responses.add(responses.POST, hook_url, status=200)

        hook = HTTPSignalHook(request_url=hook_url, request_method="post")
        post_save.connect(hook, sender=FakeModel)

        instance = FakeModel()
        instance.name = "Neapolitan"
        post_save.send(instance=instance, sender=FakeModel, created=True)

        body = json.loads(responses.calls[0].request.body)
        self.assertEqual(
            body,
            {
                "Event": "tests.fakemodel:created",
                "InstanceId": "None",
                "Instance": "eyJtb2RlbCI6ICJ0ZXN0cy5mYWtlbW9kZWwiLCAicGsiOiBudWxsLCAiZmllbGRzIjogeyJuYW1lIjogIk5lYXBvbGl0YW4ifX0=",
            },
        )

        json_instance = json.loads(base64.b64decode(body["Instance"]))
        self.assertEqual(
            json_instance,
            {"model": "tests.fakemodel", "pk": None, "fields": {"name": "Neapolitan"}},
        )
