from rest_framework import serializers

class CreditRequestSerializer(serializers.Serializer):
    amount = serializers.IntegerField(min_value=1)
