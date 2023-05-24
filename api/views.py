from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from django.http import JsonResponse
from .serializers import InstanceVMCreationSerializer, InstanceVMDecommSerializer
from gluecloud.celery import async_create_instance, async_destroy_instance


@api_view(['POST'])
def create_instance(request):
    data = JSONParser().parse(request)
    serializer = InstanceVMCreationSerializer(data=data)
    if serializer.is_valid():
        async_create_instance.delay(serializer.data)
        return JsonResponse(serializer.data, status=201)
    return JsonResponse(serializer.errors, status=400)


@api_view(['POST'])
def destroy_instance(request):
    data = JSONParser().parse(request)
    serializer = InstanceVMDecommSerializer(data=data)
    if serializer.is_valid():
        async_destroy_instance.delay(serializer.data)
        return JsonResponse(serializer.data, status=201)
    return JsonResponse(serializer.errors, status=400)