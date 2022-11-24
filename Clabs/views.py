import json

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from config.db_connection import db
from config.next_generation import generate_custom_id
import secrets
import requests


# Account CRED Operation
class Account(APIView):
    @staticmethod
    def post(request):

        request_body = request.body.decode("UTF-8")
        request_data = json.loads(request_body)

        try:

            data = {
                "name": request_data["name"],
                "email_id": request_data["email_id"],
                "status": "active",
                "key": secrets.token_hex(16)
            }

        except KeyError:
            return Response("Mandatory field is required For Creating Account", status=status.HTTP_400_BAD_REQUEST)

        # User collection
        usersc = db["account"]

        # check unique Email ID
        check_email = usersc.find_one({"email_id": data["email_id"]})

        # if not unique return error response
        if check_email:
            return Response("Email Id Already Exist!!")

        # Else unique email - creating new user
        else:
            # Generating Unique User ID
            data["acc_id"] = generate_custom_id("acc", "new")
            usersc.insert_one(data)

            del (data["_id"])

        return Response(data)

    @staticmethod
    def get(request):
        usersc = db["account"]
        # Read Operation
        data = usersc.find({"status": "active"}, {"_id": 0})
        return Response({"msg": "Read_successfully", "data": list(data)})

    @staticmethod
    def put(request):

        request_body = request.body.decode("UTF-8")
        request_data = json.loads(request_body)

        try:
            data = {
                "name": request_data["name"],
                "email_id": request_data["email_id"],
                "status": request_data["status"],
                "acc_id": request_data["acc_id"]
            }

        except KeyError:
            return Response("Mandatory field is required For Update Account", status=status.HTTP_400_BAD_REQUEST)

        usersc = db["account"]
        usersc.find_one_and_update({"acc_id": data["acc_id"]}, {"$set": data})

        return Response({"msg": "Read_successfully", "data": data})

    @staticmethod
    def delete(request):

        request_body = request.body.decode("UTF-8")
        request_data = json.loads(request_body)

        try:
            acc_id = request_data["acc_id"]

        except KeyError:
            return Response("Mandatory field is required For Update Account", status=status.HTTP_400_BAD_REQUEST)

        usersc = db["account"]
        destc = db["destination"]

        usersc.find_one_and_update({"acc_id": acc_id}, {"$set": {"status": "inactive"}})
        destc.update_many({"acc_id": acc_id}, {"$set": {"status": "inactive"}})

        return Response({"msg": "Deleted_successfully"})


# Destination CRED Operation
class Destination(APIView):
    @staticmethod
    def post(request):
        request_body = request.body.decode("UTF-8")
        request_data = json.loads(request_body)

        key = request.headers["CL-X-TOKEN"]

        try:
            data = {
                "url": request_data["url"],
                "http_method": request_data["http_method"],
                "headers": request_data["headers"],
                "params": request_data["params"],
                "status": "active"
            }
        except KeyError:
            return Response("Mandatory field is required For Creating Account", status=status.HTTP_400_BAD_REQUEST)

        data["dst_id"] = generate_custom_id("dst", "new")
        dest = db["destination"]
        usersc = db["account"]
        acc_data = usersc.find_one({"key": key, "status": "active"}, {"_id": 0})
        # User collection
        data["acc_id"] = acc_data["acc_id"]
        dest.insert_one(data)
        del (data["_id"])
        return Response(data)

    @staticmethod
    def get(request):

        acc_id = request.GET["acc_id"] if "acc_id" in request.GET else ''

        destc = db["destination"]

        # Read Operation
        if acc_id == '':
            data = destc.find({"status": "active"}, {"_id": 0})
        else:
            data = destc.find({"acc_id": acc_id, "status": "active"}, {"_id": 0})

        return Response({"msg": "Read_successfully", "data": list(data)})

    @staticmethod
    def put(request):
        request_body = request.body.decode("UTF-8")
        request_data = json.loads(request_body)

        try:
            data = {
                "url": request_data["url"],
                "http_method": request_data["http_method"],
                "status": request_data["status"],
                "acc_id": request_data["acc_id"],
                "headers": request_data["headers"],
                "params": request_data["params"],
                "dst_id": request_data["dst_id"]
            }

        except KeyError:
            return Response("Mandatory field is required For Update Destination", status=status.HTTP_400_BAD_REQUEST)

        destc = db["destination"]
        destc.find_one_and_update({"dst_id": data["dst_id"]}, {"$set": data})

        return Response({"msg": "Destination_updated_successfully", "data": data})

    @staticmethod
    def delete(request):

        request_body = request.body.decode("UTF-8")
        request_data = json.loads(request_body)

        try:
            dst_id = request_data["dst_id"]

        except KeyError:
            return Response("Mandatory field is required For Delete Destination", status=status.HTTP_400_BAD_REQUEST)

        destc = db["destination"]
        destc.find_one_and_update({"dst_id": dst_id}, {"$set": {"status": "inactive"}})

        return Response({"msg": "Deleted_successfully"})


class IncomingData(APIView):
    @staticmethod
    def post(request):
        request_body = request.body.decode("UTF-8")
        request_data = json.loads(request_body)

        key = request.headers["CL-X-TOKEN"]

        usersc = db["account"]
        destc = db["destination"]

        if key == '':
            return Response("Un Authenticate")
        else:
            acc_data = usersc.find_one({"key": key, "status": "active"}, {"_id": 0})
            if key == acc_data["key"]:
                acc_dest = destc.find({"acc_id": acc_data["acc_id"], "status": "active"}, {"_id": 0})
                dest_list = list(acc_dest)
                for i in dest_list:
                    print(i)
                    if i["http_method"] == 'post':
                        requests.post(i["url"], json.dumps(request_data), headers=i["headers"])
                    elif i["http_method"] == 'get':
                        get_data = requests.get(i['url'], params=request_data, headers=i["headers"])
                        # print("get_responce", get_data.json())
                    else:
                        requests.put(i['url'], json.dumps(request_data), headers=i["headers"])

        return Response({"data": acc_data})

    @staticmethod
    def get(request):
        request_body = request.body.decode("UTF-8")
        request_data = json.loads(request_body)

        key = request.headers["CL-X-TOKEN"]
        print(key)
        usersc = db["account"]
        destc = db["destination"]

        if key == '':
            return Response("Un Authenticate")
        else:
            data = {"name": "Joe"}

            try:
                valid_json = json.dumps(data)
            except SyntaxError as e:
                return Response("Invalid Data")

            acc_data = usersc.find_one({"key": key, "status": "active"}, {"_id": 0})

            if key == acc_data["key"]:
                acc_dest = destc.find({"acc_id": acc_data["acc_id"], "status": "active"}, {"_id": 0})
                dest_list = list(acc_dest)
                for i in dest_list:
                    print(i)
                    if i["http_method"] == 'post':
                        requests.post(i["url"], json.dumps(request_data), headers=i["headers"])
                    elif i["http_method"] == 'get':
                        get_data = requests.get(i['url'], params=request_data, headers=i["headers"])
                        # print("get_responce", get_data.json())
                    else:
                        requests.put(i['url'], json.dumps(request_data), headers=i["headers"])

        return Response({"data": data})


@api_view(["POST"])
def webhook(request):
    request_body = request.body.decode("UTF-8")
    print("Destination Account Received", request_body)
    return Response({"message": "success", "data": request_body})
