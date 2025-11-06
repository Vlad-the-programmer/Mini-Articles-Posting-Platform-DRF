from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import CustomUserDetailsSerializer
from django.contrib.auth import get_user_model
from .permissions import IsProfileOwnerORAdmin

User = get_user_model()

class UserDestroyView(generics.DestroyAPIView):
    queryset = User.objects.filter(is_active=True)
    lookup_field = 'id'
    permission_classes = [IsProfileOwnerORAdmin]
    serializer_class = CustomUserDetailsSerializer

    def perform_destroy(self, instance):
        """Soft delete by deactivating the user"""
        instance.is_active = False
        instance.save()

    def destroy(self, request, *args, **kwargs):
        """Override to provide custom response"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": "User account deactivated successfully."},
            status=status.HTTP_204_NO_CONTENT
        )