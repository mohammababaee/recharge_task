from rest_framework import serializers

class RechargeRequestSerializer(serializers.Serializer):
    amount = serializers.IntegerField(min_value=1)
    phone_number = serializers.CharField(max_length=11)
