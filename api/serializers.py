from rest_framework import serializers

class InstanceVMCreationSerializer(serializers.Serializer):
    provider = serializers.CharField(max_length=200)
    name = serializers.CharField(max_length=200)
    ami_id = serializers.CharField(max_length=200)
    instance_type = serializers.CharField(max_length=200)
    availability_zone = serializers.CharField(max_length=200)


class InstanceVMDecommSerializer(serializers.Serializer):
    provider = serializers.CharField(max_length=200)
    name = serializers.CharField(max_length=200)
    instance_id = serializers.CharField(max_length=200)
