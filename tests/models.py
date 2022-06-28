from django.db import models


class AnotherChild(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        app_label = "tests"
        db_table = "anotherChild"


class Parent(models.Model):

    name = models.CharField(max_length=100)

    child = models.ForeignKey(
        "tests.Child", on_delete=models.CASCADE, blank=True, null=True
    )
    mainChild = models.ForeignKey(
        "tests.Child", on_delete=models.CASCADE, blank=True, null=True
    )
    anotherChildren = models.ManyToManyField(
        AnotherChild, verbose_name="anotherChildren", blank=True, related_name="parent"
    )

    class Meta:
        app_label = "tests"


class Child(models.Model):
    anotherChild = models.ForeignKey(
        "tests.AnotherChild", on_delete=models.CASCADE, blank=True, null=True
    )
    name = models.CharField(max_length=100)
    desc = models.CharField(max_length=100)

    class Meta:
        app_label = "tests"
