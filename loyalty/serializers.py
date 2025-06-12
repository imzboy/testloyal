from rest_framework import serializers
from .models import Card, ExpireTerms, Transaction


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ('date', 'amount')

    def validate_amount(self, amount):
        if amount <= 0:
            raise serializers.ValidationError('Amount must be positive')
        return amount


class TransactionCreateSerializer(TransactionSerializer):
    class Meta:
        model = Transaction
        fields = TransactionSerializer.Meta.fields + ('card',)


class CardSerializer(serializers.ModelSerializer):

    expires_at = serializers.ChoiceField(choices=ExpireTerms.choices)

    class Meta:
        model = Card
        fields = (
            'id',
            'series',
            'number',
            'status',
            'balance',
            'expires_at',
        )

    def validate_expires_at(self, value):
        return ExpireTerms.validate_and_calc_expire_at(value)

    def validate_balance(self, value):
        if value < 0:
            raise serializers.ValidationError('Balance must be positive or zero')
        return value


class CardDetailsSerializer(CardSerializer):
    transactions = TransactionSerializer(many=True)

    class Meta(CardSerializer.Meta):
        fields = CardSerializer.Meta.fields + ('transactions',)
