import sys
import requests
from utils import HEADERS, PAYLOAD, AUTHCOOKIES, COOKIES


def get_csrf_token():
    global COOKIES
    response = requests.get(
        "https://www.zomato.com/webroutes/auth/csrf", headers=HEADERS
    )
    res = response.json()
    HEADERS["x-zomato-csrft"] = res["csrf"]
    COOKIES = dict(response.cookies)


def send_otp(mobile_number):
    PAYLOAD["phone"] = mobile_number
    response = requests.post(
        "https://www.zomato.com/webroutes/auth/login",
        json=PAYLOAD,
        headers=HEADERS,
        cookies=COOKIES,
    )
    res = response.json()
    return res


def login(otp, mobile_number):
    global AUTHCOOKIES
    PAYLOAD["phone"] = mobile_number
    PAYLOAD["code"] = otp
    response = requests.post(
        "https://www.zomato.com/webroutes/auth/mobile_login/verify",
        json=PAYLOAD,
        headers=HEADERS,
        cookies=COOKIES,
    )
    AUTHCOOKIES = dict(response.cookies)
    return response.json()


def fetch_orders_and_calculate_expenses():
    global AUTHCOOKIES
    params = {"page": 1}
    del HEADERS["cookie"]
    response = requests.get(
        "https://www.zomato.com/webroutes/user/orders",
        headers=HEADERS,
        cookies=AUTHCOOKIES,
        params=params,
    )
    res = response.json()
    total_pages = res["sections"]["SECTION_USER_ORDER_HISTORY"]["totalPages"]
    print(f"There are {total_pages} pages found orders")
    total_amount = 0
    for i in range(1, total_pages + 1):
        params["page"] = i
        response = requests.get(
            "https://www.zomato.com/webroutes/user/orders",
            headers=HEADERS,
            cookies=AUTHCOOKIES,
            params=params,
        )

        res = response.json()
        orders = res["entities"]["ORDER"]
        for order_id, order_dict in orders.items():
            total_amount += float(order_dict["totalCost"][1:].replace(",", ""))
        print(f"scanning page {i}")

    print("Total amount spent on zomato: ", int(total_amount))
    return total_amount


if __name__ == "__main__":
    mobile_number = sys.argv[1]
    print("Mobile Number is %s" % (mobile_number))
    get_csrf_token()
    res = send_otp(mobile_number)
    if not res["success"]:
        print(res["message"])
        sys.exit()

    print("OTP sent successfully")
    otp = input("Enter OTP: ")
    response = login(otp, mobile_number)
    if not response["success"]:
        print(response["message"])
        sys.exit()

    fetch_orders_and_calculate_expenses()
