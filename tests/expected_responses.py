NO_NESTED_FIELDS_DEFAULT_DEPTH = '{"model": "tests.parent", "pk": 1, "fields": {"name": "New Parent", "child": 1, "mainChild": 2, "anotherChildren": [1, 2]}}'

NESTED_FIELDS_DEFAULT_DEPTH = '{"model": "tests.parent", "pk": 1, "fields": {"name": "New Parent", "child": {"model": "tests.child", "pk": 1, "fields": {"anotherChild": null, "name": "Child", "desc": "Description for child1"}}, "mainChild": 2, "anotherChildren": [1, 2]}}'

NESTED_FIELDS_DEPTH_1 = '{"model": "tests.parent", "pk": 1, "fields": {"name": "New Parent", "child": {"model": "tests.child", "pk": 1, "fields": {"anotherChild": null, "name": "Child", "desc": "Description for child1"}}, "mainChild": 2, "anotherChildren": [1, 2]}}'

NESTED_FIELDS_DEPTH_2 = '{"model": "tests.parent", "pk": 1, "fields": {"name": "New Parent", "child": {"model": "tests.child", "pk": 1, "fields": {"anotherChild": null, "name": "Child", "desc": "Description for child1"}}, "mainChild": 2, "anotherChildren": [{"model": "tests.anotherchild", "pk": 1, "fields": {"name": "Another Child 1"}}, {"model": "tests.anotherchild", "pk": 2, "fields": {"name": "Another Child 2"}}]}}'

ARRAY_NESTED_FIELDS_DEPTH_1 = '{"model": "tests.parent", "pk": 1, "fields": {"name": "New Parent", "child": 1, "mainChild": 2, "anotherChildren": [{"model": "tests.anotherchild", "pk": 1, "fields": {"name": "Another Child 1"}}, {"model": "tests.anotherchild", "pk": 2, "fields": {"name": "Another Child 2"}}]}}'
