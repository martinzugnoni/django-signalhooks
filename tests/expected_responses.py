NO_NESTED_FIELDS_DEFAULT_DEPTH = {
    "model": "tests.parent",
    "pk": 1,
    "fields": {
        "name": "New Parent",
        "child": 1,
        "main_child": 2,
        "another_children": [1, 2],
    },
}

NESTED_FIELDS_DEFAULT_DEPTH = {
    "model": "tests.parent",
    "pk": 1,
    "fields": {
        "name": "New Parent",
        "child": {
            "model": "tests.child",
            "pk": 1,
            "fields": {
                "another_child": None,
                "name": "Child",
                "desc": "Description for child1",
            },
        },
        "main_child": 2,
        "another_children": [1, 2],
    },
}

NESTED_FIELDS_DEPTH_1 = {
    "model": "tests.parent",
    "pk": 1,
    "fields": {
        "name": "New Parent",
        "child": {
            "model": "tests.child",
            "pk": 1,
            "fields": {
                "another_child": None,
                "name": "Child",
                "desc": "Description for child1",
            },
        },
        "main_child": 2,
        "another_children": [1, 2],
    },
}

NESTED_FIELDS_DEPTH_2 = {
    "model": "tests.parent",
    "pk": 1,
    "fields": {
        "name": "New Parent",
        "child": {
            "model": "tests.child",
            "pk": 1,
            "fields": {
                "another_child": None,
                "name": "Child",
                "desc": "Description for child1",
            },
        },
        "main_child": 2,
        "another_children": [
            {
                "model": "tests.anotherchild",
                "pk": 1,
                "fields": {"name": "Another Child 1"},
            },
            {
                "model": "tests.anotherchild",
                "pk": 2,
                "fields": {"name": "Another Child 2"},
            },
        ],
    },
}

ARRAY_NESTED_FIELDS_DEPTH_1 = {
    "model": "tests.parent",
    "pk": 1,
    "fields": {
        "name": "New Parent",
        "child": 1,
        "main_child": 2,
        "another_children": [
            {
                "model": "tests.anotherchild",
                "pk": 1,
                "fields": {"name": "Another Child 1"},
            },
            {
                "model": "tests.anotherchild",
                "pk": 2,
                "fields": {"name": "Another Child 2"},
            },
        ],
    },
}
