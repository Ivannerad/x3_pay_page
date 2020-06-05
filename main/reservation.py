import requests
import datetime

# Аутентификация на x3
headers = {
    'authority': 'x3club.app.enes.tech',
    'accept': 'application/json, text/plain, */*',
    'sec-fetch-dest': 'empty',
    'accept-language': 'ru',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
    'origin': 'https://x3club.admin.enes.tech',
    'sec-fetch-site': 'same-site',
    'sec-fetch-mode': 'cors',
    'referer': 'https://x3club.admin.enes.tech/authentication/login',
}
data = {"username": "parser", "password": "parser1", "grant_type": "password", "client_id": "test"}

x3_response = requests.post('https://x3club.app.enes.tech/api/v2/user/admin_auth/', headers=headers, data=data)
token = x3_response.json()["token"]
headers['authorization'] = 'Token %s' % token
headers['referer'] = 'https://x3club.admin.enes.tech/users/list'

def get_active_cashdesk():
    URL = "https://x3club.app.enes.tech/api/v2/cashdesk_office/"
    response = requests.get(url=URL, headers=headers)
    results = response.json()['results'][0]
    cashdesks = results['cashdesks']
    cashdesk = [item for item in cashdesks if item['has_employee_session'] and item['has_cashdesk_session'] and item['name']=='x3club']
    # {id: 2, devid: "072812", name: "Штрих", is_online: false, has_employee_session: false,…}
    if len(cashdesk) > 0:
        return cashdesk[0]
    else:
        pass # error: no open cashdesk

def get_account_id(login):
    URL = f"https://x3club.app.enes.tech/api/v2/short_account/?search={login}"
    response = requests.get(url=URL, headers=headers)
    results = response.json()['results']
    if len(results) > 0:
        account_id = results[0]['account_id']
        return account_id
    else:
        pass # error: no account with login

def refill_account(cashdesk, account_id, amount):
    URL = "https://x3club.app.enes.tech/api/v2/refill_account/"
    referer = f"https://x3club.admin.enes.tech/cashbox/o/1/{cashdesk['id']}/refill/account"
    headers['referer'] = referer
    data = {"devid": cashdesk['devid'], "account_id": account_id, "amount": amount, "payment_type": 1} # payment_type=0 - cash, payment_type=1 - card
    response = requests.post(url=URL, data=data, headers=headers)
    if response.status_code == 200:
        results = response.json()['data']
        check_code = results['check_code']
        check_amount = results['check_amount']
        payment_date = results['payment_date']
    else:
        pass # error: no payment

def get_workstation_id(account_id):
    URL = "https://x3club.app.enes.tech/api/v2/booking/reservation/grid/?office_id=1"
    referer = "https://x3club.admin.enes.tech/reservation/schedule?office_id=1"
    headers['referer'] = referer
    response = requests.get(url=URL, headers=headers)
    results = response.json()['results']
    for item in results:
        account_reserv = [reserv for reserv in item['grouped_reservations'] if reserv['account_id'] == account_id]
        print(account_reserv, end='======================\n')
        if len(account_reserv) > 0:
            workstation_id = item['workstation_id']
            start_date = account_reserv[-1]['end_date'] # "2020-04-29T13:00:00Z"
            print(start_date)
            return workstation_id, start_date
    else:
        pass # error: no reservation

def booking_reservation(login, workstation_id, start_date, time):
    end_date = (datetime.datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%SZ") + datetime.timedelta(hours=time)).strftime("%Y-%m-%dT%H:%M:%SZ")
    data = {"workstation_id": workstation_id, "start_date": start_date, "end_date": end_date, "account_login": login, "description": ""}
    # booking/reservation/information
    login = login.replace('+', '%2B') # replace + in +79210000000 on utf-8 code. Else raises error in api.
    URL = f"https://x3club.app.enes.tech/api/v2/booking/reservation/information/?workstation_id={workstation_id}&start_date={start_date}&end_date={end_date}&account_login={login}"
    response = requests.get(url=URL, headers=headers)
    results = response.json()
    if results['account_balance'] >= results['payable_amount']:
        # booking/reservation
        URL = "https://x3club.app.enes.tech/api/v2/booking/reservation/"
        response = requests.post(url=URL, data=data, headers=headers)
        print(response)
        if response.status_code == 201:
            pass # success
        else:
            pass # error
    else:
        pass # error: not enough money

def continue_play(login, amount, time):
    ''' Account refill and continue booking. If need booking, just on it. '''
    account_id = get_account_id(login)
    cashdesk = get_active_cashdesk()
    refill_account(cashdesk, account_id, amount)
#    workstation_id, start_date = get_workstation_id(account_id)
#    booking_reservation(login, workstation_id, start_date, time)

