from rest_framework import serializers
from .models import BudgetLine


class BudgetLineSerializer(serializers.ModelSerializer):
    suma_cheltuita = serializers.ReadOnlyField()
    suma_ramasa = serializers.ReadOnlyField()
    procent_cheltuit = serializers.ReadOnlyField()

    class Meta:
        model = BudgetLine
        fields = [
            'id', 'cod_bugetar', 'denumirea', 'suma_alocata', 'anul',
            'suma_cheltuita', 'suma_ramasa', 'procent_cheltuit', 'file_name',
            'created_at'
        ]