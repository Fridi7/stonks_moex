from rest_framework import serializers


class QuotedSecuritiesSerializer(serializers.Serializer):
    trade_data = serializers.DateField()
    secid = serializers.CharField(max_length=36)
    name = serializers.CharField(max_length=765)
    isin = serializers.CharField(max_length=765)
    reg_number = serializers.CharField(max_length=189)
    main_board_id = serializers.CharField(max_length=12)
    list_level = serializers.CharField(max_length=6)
    quoted = serializers.BooleanField()


class StocksSerializer(serializers.Serializer):
    trade_data = serializers.DateField()
    close = serializers.FloatField()
    board_id = serializers.CharField(max_length=12)


class SummarySerializer(serializers.Serializer):
    name = serializers.CharField(max_length=765)
    secid = serializers.CharField(max_length=36)
    board_id = serializers.CharField(max_length=12)
    pct_change = serializers.FloatField()
