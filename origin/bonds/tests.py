from django.contrib.auth.models import User
from bonds.models import Bond
from rest_framework.test import APISimpleTestCase, APITestCase
from django.test import Client
import json


class HelloWorld(APISimpleTestCase):
    def test_root(self):
        resp = self.client.get("/")
        assert resp.status_code == 200


class BondsTest(APITestCase):
    def setup(self, data):
        self.username = "test" + data + "@origin.com"
        self.password = "foorbar123"+ data
        user = User.objects.create_user(username=self.username)
        user.set_password(self.password)
        user.save()
        Bond.objects.create(isin="FR0000131104", size=100000000, currency="EUR", maturity="2025-02-28",
                            lei="something_bad", legal_name="bond", user=user)
        Bond.objects.create(isin="isin_test", size=1, currency="CUR", maturity="2000-02-28",
                            lei="something_else", legal_name="bond_test", user=user)
        c = Client()
        c.login(username=self.username, password=self.password)
        return c, user

    def test_post_unauthorized(self):
        resp = self.client.post("/bonds/")

        assert resp.status_code == 401

    def test_post_authorized_with_good_data(self):
        self.client, self.user = self.setup("origin")
        payload = json.dumps({
            "isin": "FR0000131104",
            "size": 100000000,
            "currency": "EUR",
            "maturity": "2025-02-28",
            "lei": "R0MUWSFPU8MPRO8K5P83",
        })
        resp = self.client.post("/bonds/", data=payload, content_type="application/json",
                                HTTP_AUTHORIZATION='Token {}'.format(self.user.auth_token))
        self.assertEqual(resp.status_code, 201)

    def test_post_authorized_with_bad_data(self):
        self.client, self.user = self.setup("origin")
        payload = json.dumps({
            "bad": "data",
        })
        resp = self.client.post("/bonds/", data=payload, content_type="application/json",
                                HTTP_AUTHORIZATION='Token {}'.format(self.user.auth_token))
        self.assertEqual(resp.status_code, 400)

    def test_post_authorized_with_invalid_lei(self):
        self.client, self.user = self.setup("origin")
        payload = json.dumps({
            "isin": "FR0000131104",
            "size": 100000000,
            "currency": "EUR",
            "maturity": "2025-02-28",
            "lei": "something_bad",
        })
        resp = self.client.post("/bonds/", data=payload, content_type="application/json",
                                HTTP_AUTHORIZATION='Token {}'.format(self.user.auth_token))
        self.assertEqual(resp.status_code, 400)

    def test_bond_legal_name(self):
        self.client, self.user = self.setup("origin")
        payload = json.dumps({
            "isin": "FR0000131104",
            "size": 100000000,
            "currency": "EUR",
            "maturity": "2025-02-28",
            "lei": "R0MUWSFPU8MPRO8K5P83",
        })
        resp = self.client.post("/bonds/", data=payload, content_type="application/json",
                                HTTP_AUTHORIZATION='Token {}'.format(self.user.auth_token))
        b = Bond.objects.get(lei="R0MUWSFPU8MPRO8K5P83")
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(getattr(b, 'legal_name'), "BNP PARIBAS")

    def test_get_all(self):
        self.client, self.user = self.setup("origin")
        resp = self.client.get("/bonds/", HTTP_AUTHORIZATION='Token {}'.format(self.user.auth_token))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 2)

    def test_get_authorized(self):
        user0 = User.objects.create_user(username="test0")
        user0.set_password("password0")
        user0.save()
        Bond.objects.create(isin="test_0", size=100000000, currency="EUR", maturity="2025-02-28",
                            lei="test_0", legal_name="test_0", user=user0)

        self.client, self.user = self.setup("origin")
        resp = self.client.get("/bonds/", HTTP_AUTHORIZATION='Token {}'.format(self.user.auth_token))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 2)

    def test_get_filtered_size(self):
        self.client, self.user = self.setup("origin")
        resp = self.client.get("/bonds/", {'size': "1"},
                               HTTP_AUTHORIZATION='Token {}'.format(self.user.auth_token))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 1)

    def test_get_filtered_isin(self):
        self.client, self.user = self.setup("origin")
        resp = self.client.get("/bonds/", {'isin': "isin_test"},
                               HTTP_AUTHORIZATION='Token {}'.format(self.user.auth_token))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 1)

    def test_get_filtered_currency(self):
        self.client, self.user = self.setup("origin")
        resp = self.client.get("/bonds/", {'currency': "CUR"},
                               HTTP_AUTHORIZATION='Token {}'.format(self.user.auth_token))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 1)

    def test_get_filtered_maturity(self):
        self.client, self.user = self.setup("origin")
        resp = self.client.get("/bonds/", {'maturity': "2000-02-28"},
                               HTTP_AUTHORIZATION='Token {}'.format(self.user.auth_token))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 1)

    def test_get_filtered_lei(self):
        self.client, self.user = self.setup("origin")
        resp = self.client.get("/bonds/", {'lei': "something_else"},
                               HTTP_AUTHORIZATION='Token {}'.format(self.user.auth_token))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 1)

    def test_get_filtered_legal_name(self):
        self.client, self.user = self.setup("origin")
        resp = self.client.get("/bonds/", {'legal_name': "bond_test"},
                               HTTP_AUTHORIZATION='Token {}'.format(self.user.auth_token))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 1)
