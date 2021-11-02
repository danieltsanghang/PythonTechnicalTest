from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser
from rest_framework import status
from bonds.serializers import BondSerializer
import requests

from .models import Bond

look_up = 'https://api.gleif.org/api/v1/lei-records/{}'
payload = {}
headers = {
    'Accept': 'application/vnd.api+json'
}


class HelloWorld(APIView):
    def get(self, request):
        return Response("Hello World!")


class BondJSON(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data = JSONParser().parse(request)
        try:
            r = requests.request('GET', url=look_up.format(data['lei']), data=payload, headers=headers)
        except KeyError as e:
            return Response("No lei provided", status=status.HTTP_400_BAD_REQUEST)
        if r.status_code != requests.codes.ok:
            return Response("No entry with lei={}".format(data['lei']), status=status.HTTP_400_BAD_REQUEST)

        data['legal_name'] = r.json()['data']['attributes']['entity']['legalName']['name']

        data['user'] = request.user.id
        bond_serializer = BondSerializer(data=data)
        if bond_serializer.is_valid():
            bond_serializer.save()
            return Response(status=status.HTTP_201_CREATED)

        return Response(bond_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        bonds = Bond.objects.all().filter(user=request.user.id)
        for k, v in request.GET.items():
            if k == 'isin':
                bonds = bonds.filter(isin=v)
            elif k == "size":
                bonds = bonds.filter(size=v)
            elif k == "currency":
                bonds = bonds.filter(currency=v)
            elif k == "maturity":
                bonds = bonds.filter(maturity=v)
            elif k == "lei":
                bonds = bonds.filter(lei=v)
            elif k == "legal_name":
                bonds = bonds.filter(legal_name=v)

        tutorials_serializer = BondSerializer(bonds, many=True)
        return JsonResponse(tutorials_serializer.data, safe=False)
