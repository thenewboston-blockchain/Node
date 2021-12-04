from djongo.models.fields import JSONField


class NullableJSONField(JSONField):

    def get_prep_value(self, value):
        if value is not None and not isinstance(value, (dict, list)):
            raise ValueError(f'Value: {value} must be of type dict/list')
        return value

    def to_python(self, value):
        if value is not None and not isinstance(value, (dict, list)):
            raise ValueError(f'Value: {value} stored in DB must be of type dict/list' 'Did you miss any Migrations?')
        return value
