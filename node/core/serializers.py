from rest_framework.exceptions import ValidationError


class ValidateUnknownFieldsMixin:

    def validate(self, attrs):
        """
        Make front-end developers life easier when they make a typo in an
        optional attribute name.
        """
        attrs = super().validate(attrs)

        # TODO(dmu) MEDIUM: Nested serializers do not have `initial_data` (why?).
        #                   Produce a fix instead of current workaround
        if hasattr(self, 'initial_data') and (unknown := set(self.initial_data).difference(self.fields)):
            raise ValidationError(f'Unknown field(s): {", ".join(sorted(unknown))}')

        return attrs
