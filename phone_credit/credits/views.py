from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .permission import IsSellerUser
from .services import CreditService
from .serializers import CreditRequestSerializer

class CreditRequestView(APIView):
    permission_classes = [IsAuthenticated, IsSellerUser]

    def post(self, request):
        serializer = CreditRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            credit = CreditService.increase_credit(amount=serializer.validated_data['amount'], user=request.user)
            return Response({"status": "ok", "id": credit.id}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)