from rest_framework import serializers

class CreditRequestSerializer(serializers.Serializer):
    amount = serializers.IntegerField(min_value=1)

class ApproveCreditSerializer(serializers.Serializer):
    request_id = serializers.IntegerField(min_value=1)