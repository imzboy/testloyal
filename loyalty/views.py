from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction

from .models import Card, CardStatus
from .serializers import CardDetailsSerializer, CardSerializer, TransactionCreateSerializer


class CardViewViewSet(ModelViewSet):
    queryset = Card.objects.all()
    serializer_class = CardSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        'series',
        'number',
        'status',
        'issued_at',
        'expires_at',
    ]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CardDetailsSerializer
        elif self.action == 'create_transaction':
            return TransactionCreateSerializer
        return super().get_serializer_class()

    @action(detail=True, methods=['post'])
    def activate(self, request, *args, **kwargs):
        with transaction.atomic():
            card = Card.objects.select_for_update().get(pk=self.kwargs['pk'])
            if card.is_expired():
                return Response({'error': f'Card is expired'}, status=status.HTTP_400_BAD_REQUEST)
            card.status = CardStatus.ACTIVE.value
            card.save()
            return self.retrieve(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def deactivate(self, request, *args, **kwargs):
        with transaction.atomic():
            card = Card.objects.select_for_update().get(pk=self.kwargs['pk'])
            if card.is_expired():
                return Response({'error': f'Card is expired'}, status=status.HTTP_400_BAD_REQUEST)
            card.status = CardStatus.INACTIVE.value
            card.save()
            return self.retrieve(request, *args, **kwargs)

    @action(detail=True, methods=['post'], url_path='transactions')
    def create_transaction(self, request, *args, **kwargs):
        with transaction.atomic():
            card = Card.objects.select_for_update().get(pk=self.kwargs['pk'])
            data = request.data.copy()
            if card.is_inactive() or card.is_expired():
                return Response({'error': f'Card is {card.status}'}, status=status.HTTP_400_BAD_REQUEST)

            data['card'] = card.id
            serializer = TransactionCreateSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            card.balance += serializer.validated_data['amount']
            card.save(update_fields=['balance'])

            return Response(serializer.data, status=status.HTTP_201_CREATED)
