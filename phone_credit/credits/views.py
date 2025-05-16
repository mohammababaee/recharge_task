from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .permission import IsAdminUser, IsSellerUser
from .services import CreditService
from .serializers import ApproveCreditSerializer, CreditRequestSerializer

class CreditRequestView(APIView):
    permission_classes = [IsSellerUser]

    def post(self, request):
        serializer = CreditRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            credit = CreditService.increase_credit(amount=serializer.validated_data['amount'], user=request.user)
            return Response({"status": "ok", "id": credit.id}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class ApproveCreditView(APIView):
    permission_classes = [IsAdminUser]

    def post(self,request):
        serializer = ApproveCreditSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            credit = CreditService.approve_request(request_id=serializer.validated_data['request_id'])
            return Response({"status": "Done"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)