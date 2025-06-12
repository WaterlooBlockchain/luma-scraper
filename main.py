import requests
import json
import sys
import pandas as pd
from io import StringIO
from dotenv import load_dotenv
import os

device_headers = {
    'Host': 'api.lu.ma',
    'sec-ch-ua-platform': '"macOS"',
    'accept-language': 'en',
    'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
    'x-luma-client-type': 'luma-web',
    'accept': '*/*',
    'origin': 'https://lu.ma',
    'sec-fetch-site': 'same-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://lu.ma/',
    'priority': 'u=1, i'
}

def send_otp(email):
    print("Logging in")

    url = "https://api.lu.ma/auth/email/start-with-email"

    payload = json.dumps({
        "email": email
    })

    headers = {
    'Cookie': 'luma.first-page=%2Fhome',
    'x-luma-web-url': 'https://lu.ma/signin?next=%2Fhome',
    'content-type': 'application/json',
    'x-luma-previous-path': '/home',
    'sec-fetch-site': 'same-site',
    **device_headers
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    match response.status_code:
        case 200:
            print("Sent OTP request to email")
        case _:
            print(f"Unknown error, status code: {response.status_code}")
            sys.exit(1)


def sumbit_otp(email, otp):
    print("Submitting OTP")

    url = "https://api.lu.ma/auth/email/sign-in-with-code"

    payload = json.dumps({
        "email": email,
        "code": otp
    })

    headers = {
    'Cookie': 'luma.first-page=%2Fhome',
    'x-luma-web-url': 'https://lu.ma/signin?next=%2Fhome',
    'content-type': 'application/json',
    'x-luma-previous-path': '/home',
    **device_headers
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    match response.status_code:
        case 200:
            print("Logged in")
            response_json = response.json()

            auth_token = response_json["auth_token"]
            api_id = response_json["api_id"]
            #centrifugo_user_token = response_json["centrifugo_user_token"]
            return auth_token, api_id
        case _:
            print(f"Unknown error, status code: {response.status_code}")
            sys.exit(1)

def fetch_events(auth_token, api_id):
    print("Fetching event list")

    url = "https://api.lu.ma/search/get-results?query="

    headers = {
    'Cookie': f'luma.native-referrer=https%3A%2F%2Fwww.google.com%2F; luma.first-page=%2Fhome; luma.auth-session-key={auth_token};',
    'x-luma-web-url': 'https://lu.ma/signin?next=%2Fhome',
    'x-luma-previous-path': '/home',
    **device_headers
    }

    response = requests.request("GET", url, headers=headers)

    event_list = []

    match response.status_code:
        case 200:
            print("Fetched event list")

            response_json = response.json()

            for event in response_json["events"]:                
                for host in event["hosts"]:
                    if host["api_id"] == api_id and host["access_level"] == "manager":
                        event_api_id = host["event_api_id"]
                        event_list.append(event_api_id)

            return event_list
                        
        case _:
            print(f"Unknown error, status code: {response.status_code}")

def fetch_download_url(auth_token, event_api_id):
    print("Fetching event csv download url")

    url = f"https://api.lu.ma/event/admin/download-guests-csv?event_api_id={event_api_id}"

    headers = {
    'x-luma-client-type': 'luma-web',
    'x-luma-client-version': 'f059af82310ed04acf46a75eae5f4d6a9d68b42c',
    'x-luma-web-url': 'https://lu.ma/event/manage/evt-/guests',
    'Cookie': f'luma.first-page=%2F; luma.auth-session-key={auth_token}; luma.native-referrer=https%3A%2F%2Flu.ma%2Fhome;',
    **device_headers
    }

    response = requests.request("GET", url, headers=headers)

    match response.status_code:
        case 200:
            print("Fetched csv url")

            response_json = response.json()

            download_url = response_json["download_url"]
            return download_url
        case 444:
            print("Cloudflare block :(, saving event_api_id in failed.txt retry with retry mode")
            with open('failed.txt', 'a') as file:
                file.write(event_api_id + '\n')
        case _:
            print(f"Unknown error, status code: {response.status_code}")

def download_csv(url):
    print("Downloading event csv")

    response = requests.request("GET", url)

    match response.status_code:
        case 200:
            print("Fetched csv")
            return response.text
        case _:
            print(f"Unknown error, status code: {response.status_code}")


def main():
    load_dotenv()
    output_file = "guests.csv"
    email = os.getenv("EMAIL")

    print("Welcome to Luma Scraper \nPlease select from one of the modes below \n Mode 1: Fetch emails \n Mode 2: Fetch failed emails")

    while True:
        mode = input("Enter the mode you wish to run (1 or 2): ")
        if mode != "1" and mode != "2":
            print("Please enter a valid input")
            continue
        else:
            mode = int(mode)
            break

    match mode:
        case 1:
            send_otp(email)
            otp = input("Enter the OTP sent to your email: ")
            auth_token, api_id = sumbit_otp(email, otp)
            event_list = fetch_events(auth_token, api_id)

            download_urls = []

            for event in event_list:
                download_url = fetch_download_url(auth_token, event)
                download_urls.append(download_url)

            for url in download_urls:
                csv = download_csv(url)
                df = pd.read_csv(StringIO(csv))
                filtered_df = df[["email"]].copy()
                filtered_df.to_csv(output_file, mode="a", index=False, header=False)

            print("Emails saved, if you had any Cloudflare blocks please re-run with mode 2")     
        case 2:
            send_otp(email)
            otp = input("Enter the OTP sent to your email: ")
            auth_token, api_id = sumbit_otp(email, otp)

            with open('failed.txt', 'r') as file:
                event_list = file.readlines()

            download_urls = []

            for event in event_list:
                download_url = fetch_download_url(auth_token, event)
                download_urls.append(download_url)

            for url in download_urls:
                csv = download_csv(url)
                df = pd.read_csv(StringIO(csv))
                filtered_df = df[["email"]].copy()
                filtered_df.to_csv(output_file, mode="a", index=False, header=False)

            print("Emails saved, if you had any Cloudflare blocks please re-run with mode 2")     

if __name__ == "__main__":
    main()    