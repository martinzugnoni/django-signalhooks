import json
import base64
import boto3
import requests

from django.core.serializers import serialize
from django.contrib.contenttypes.models import ContentType


class SignalHook:
    def __call__(self, signal, sender, **kwargs):
        pass

    def serialize_instance(self, instance):
        """
        Serializes given Model instance as JSON and encodes it as base64.
        """
        json_instance = serialize("json", [instance], ensure_ascii=False)[1:-1]
        return base64.b64encode(json_instance.encode("utf-8")).decode("utf-8")


class HTTPSignalHook(SignalHook):
    def __init__(
        self, request_url, request_method="post", **kwargs,
    ):
        self.request_url = request_url
        self.request_method = request_method

    def get_request_url_params(self):
        return {}

    def get_request_url_headers(self):
        return {"Content-Type": "application/json"}

    def get_request_payload(self, instance=None, created=None):
        if not all([instance, created]):
            return {}

        ct = ContentType.objects.get_for_model(instance)
        return {
            "Event": f"{ct.app_label}.{ct.model}:{'created' if created else 'updated'}",
            "InstanceId": str(instance.id),
            "Instance": self.serialize_instance(instance),
        }

    def __call__(self, signal, sender, **kwargs):
        """
        Receiver function executed when a Django Signal is triggered.
        """
        payload = self.get_request_payload(
            instance=kwargs.get("instance"), created=kwargs.get("created")
        )
        requests.request(
            method=self.request_method,
            url=self.request_url,
            params=self.get_request_url_params(),
            headers=self.get_request_url_headers(),
            data=json.dumps(payload),
        )


class SNSSignalHook(SignalHook):
    def __init__(
        self,
        sns_topic_arn,
        aws_access_key=None,
        aws_secret_key=None,
        aws_region="us-east-1",
        **kwargs,
    ):
        self.aws_access_key = aws_access_key
        self.aws_secret_key = aws_secret_key
        self.aws_region = aws_region
        self.sns_topic_arn = sns_topic_arn

    def get_sns_client(self):
        params = {"region_name": self.aws_region}
        if all([self.aws_access_key, self.aws_secret_key]):
            params.update(
                {
                    "aws_access_key_id": self.aws_access_key,
                    "aws_secret_access_key": self.aws_secret_key,
                }
            )
        return boto3.client("sns", **params)

    def get_sns_msg(self):
        return "Django Signal triggered"

    def get_sns_msg_attributes(self, instance=None, created=None):
        if not all([instance, created]):
            return {}

        ct = ContentType.objects.get_for_model(instance)
        return {
            "Event": {
                "DataType": "String",
                "StringValue": f"{ct.app_label}.{ct.model}:{'created' if created else 'updated'}",
            },
            "InstanceId": {"DataType": "String", "StringValue": str(instance.id),},
            "Instance": {
                "DataType": "String",
                "StringValue": self.serialize_instance(instance),
            },
        }

    def __call__(self, signal, sender, **kwargs):
        """
        Receiver function executed when a Django Signal is triggered.
        """
        msg_attributes = self.get_sns_msg_attributes(
            instance=kwargs.get("instance"), created=kwargs.get("created")
        )

        sns_client = self.get_sns_client()
        sns_client.publish(
            TopicArn=self.sns_topic_arn,
            Message=self.get_sns_msg(),
            MessageAttributes=msg_attributes,
        )
