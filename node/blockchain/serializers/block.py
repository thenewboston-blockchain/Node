from rest_framework import serializers

from node.blockchain.models import Block as ORMBlock


class BlockSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        return instance.body

    class Meta:
        model = ORMBlock
        fields = ('_id',)  # we are faking list of fields here
