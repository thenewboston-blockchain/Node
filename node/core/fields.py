from djongo.models.fields import JSONField as DjongoJSONField
from rest_framework.fields import JSONField as DRFJSONField


class NullableJSONField(DjongoJSONField):

    def get_prep_value(self, value):
        if value is not None and not isinstance(value, (dict, list)):
            raise ValueError(f'Value: {value} must be of type dict/list')
        return value

    def to_python(self, value):
        if value is not None and not isinstance(value, (dict, list)):
            raise ValueError(f'Value: {value} stored in DB must be of type dict/list' 'Did you miss any Migrations?')
        return value


class PydanticModelBackedJSONField(DRFJSONField):

    def to_representation(self, value):
        if self.binary:
            if self.encoder is not None:
                raise NotImplementedError('Custom encoder is not supported')

            return value.json().encode()

        # TODO(dmu) MEDIUM: The representation is not crypto friendly (key order, separators, ect). Should we fix it?
        return value.dict()
