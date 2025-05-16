from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from credits.permission import IsSellerUser
from recharges.serializers import RechargeRequestSerializer
from recharges.services import RechargePhoneNumberService

class RechargeView(APIView):
    permission_classes = [IsSellerUser]

    def post(self,request):
        serializer = RechargeRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            phone_number = RechargePhoneNumberService.charge_phone_number(
                request.user,
                amount=serializer.validated_data['amount'],
                phone_number=serializer.validated_data['phone_number']
                )
            return Response({"status": "Done", "description": f"{phone_number} charged {serializer.validated_data['amount']} toman"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)