from flask import Flask, render_template,request
import requests
import json
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
# from ibm_platform_services.iam_identity_v1 import *
from ibm_platform_services import IamIdentityV1
import config

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/form")
def form():
    return render_template("form.html")

@app.route('/result',methods =["GET", "POST"])
def result():
    form_input = request.form.to_dict()
    if len(form_input) != 0:
        if (form_input["state"] != "NJ"):
            return render_template("noresult.html", message = "Sorry, our application currently only supports residents in New Jersey. Please check back again for further updates.")
        else:
            #access token
            headers_token = {
                'accept': 'application/json',
            }

            data_token = {
                'grant_type': 'urn:ibm:params:oauth:grant-type:apikey',
                'apikey': config.api_key
            }

            response_token = requests.post('https://iam.cloud.ibm.com/identity/token', headers=headers_token, data=data_token)
            json_object = json.loads(response_token.text)

            #fetch api
            headers = {
            'accept': 'application/json',
            'authorization': 'Bearer ' + json_object["access_token"],
            }
            params = {
                'blocking': 'true',
            }
            data = {
                "race": form_input["Race"], 
                "county": form_input["county"]
            }

            response = requests.post('https://us-east.functions.cloud.ibm.com/api/v1/namespaces/26095e4b-8f64-4b8f-b1b6-59b7376c4898/actions/vaccine-algo-api-1', params=params, json = data, headers=headers)
            response = dict(json.loads(response.text))
            response=response["response"]["result"]
            address = response["address"]
            url="http://maps.google.com/maps?q="
            for i in address.split():
                url = url + "+" +i
                
            if (response['provider'] == "Unavailable"):
                return render_template("noresult.html", message="Sorry, no provider is available to you at the moment. Please check back again later.")
            else:           
                return render_template("result.html", response=response, url=url)
    return render_template("form.html")

@app.route("/info")

def info():
    return render_template("info.html")


if __name__=="__main__":
    app.run(debug=True)


