from django.db import models


class AnotherChild(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        app_label = "tests"
        db_table = "another_child"


class Parent(models.Model):

    name = models.CharField(max_length=100)

    child = models.ForeignKey(
        "tests.Child", on_delete=models.CASCADE, blank=True, null=True
    )
    main_child = models.ForeignKey(
        "tests.Child", on_delete=models.CASCADE, blank=True, null=True
    )
    another_children = models.ManyToManyField(
        AnotherChild, verbose_name="another_children", blank=True, related_name="parent"
    )

    class Meta:
        app_label = "tests"


class Child(models.Model):
    another_child = models.ForeignKey(
        "tests.AnotherChild", on_delete=models.CASCADE, blank=True, null=True
    )
    name = models.CharField(max_length=100)
    desc = models.CharField(max_length=100)

    class Meta:
        app_label = "tests"
