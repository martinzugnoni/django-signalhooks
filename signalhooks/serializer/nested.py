from django.core.serializers.json import Serializer as JsonSerializer
from django.db.models.fields.related import ForeignKey
from django.utils.encoding import is_protected_type


class Serializer(JsonSerializer):
    def __init__(self):
        super().__init__()
        self._max_depth = 0
        self._level = 0
        self._nested_fields = []
        self._current = None

    def _init_options(self):
        """
        Extract nested_fields and max_depth parameters, stores them in the instance 
        and calls super()._init_options().
        """
        self._max_depth = self.options.pop("max_depth", 0)
        self._nested_fields = self.options.pop("nested_fields", [])
        super()._init_options()

    def m2m_full_object(self, obj):
        """
        Serializes a full object instance that belongs to a ManyToMany relationship.
        """
        self._level += 1
        aux = self._current
        value = self.serialize_fk(obj)
        self._current = aux
        self._level -= 1
        return value

    def handle_m2m_field(self, obj, field):
        """
        We override this method to check if the ManyToMany attribute is required to be serialized or not.
        We call custom serialization if needed.
        """
        if field.remote_field.through._meta.auto_created:
            if field.name not in self._nested_fields or self._level > self._max_depth:

                def m2m_value(value):
                    return self._value_from_field(value, value._meta.pk)

            else:

                def m2m_value(value):
                    return self.m2m_full_object(value)

            self._current[field.name] = [
                m2m_value(related) for related in getattr(obj, field.name).iterator()
            ]

    def _value_from_field(self, obj, field):
        """
        This method overrides the default behaviour for ForeingKey and
        returns full object if needed. The rest of the behaviour remains the same.
        """
        if isinstance(field, ForeignKey):
            self._level += 1
            aux = self._current
            value = self.serialize_fk(getattr(obj, field.name))
            self._current = aux
            self._level -= 1
            return value
        value = field.value_from_object(obj)
        if is_protected_type(value):
            return value
        return field.value_to_string(obj)

    def handle_fk_field(self, obj, field):
        """
        Decides if we need to call custom or default serialization based on _nested_fields 
        and max_depth.
        """
        if self._level > self._max_depth or field.name not in self._nested_fields:
            value = super()._value_from_field(obj, field)
        else:
            value = self._value_from_field(obj, field)
        self._current[field.name] = value

    def serialize_fk(self, o):
        """
        Overrides default serialization to call the new methods for ForeingKey and m2m. 
        """
        self.start_object(o)
        concrete_model = o._meta.concrete_model
        for field in concrete_model._meta.local_fields:
            if field.serialize or field is None:
                if field.remote_field is None:
                    if (
                        self.selected_fields is None
                        or field.attname in self.selected_fields
                    ):
                        self.handle_field(o, field)
                else:
                    if (
                        self.selected_fields is None
                        or field.attname[:-3] in self.selected_fields
                    ):
                        self.handle_fk_field(o, field)
        for field in concrete_model._meta.local_many_to_many:
            if field.serialize:
                if (
                    self.selected_fields is None
                    or field.attname in self.selected_fields
                ):
                    self.handle_m2m_field(o, field)
        value = self.get_dump_object(o)
        return value
