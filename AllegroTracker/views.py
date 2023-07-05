import requests
import json
import threading
import time

from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO
from matplotlib import pyplot

from validate_email import validate_email
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Product, Price
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib import messages
from django.core.mail import EmailMessage
from django.views import View
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.core.paginator import Paginator

from schedule import Scheduler
from .utils import token_generation
# from .apps import ACCESS_TOKEN
import os
from dotenv import load_dotenv

CLIENT_ID = str(os.environ.get('CLIENT_ID'))
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
ACCESS_TOKEN = ""

PREFIX_URL = "https://api.allegro.pl.allegrosandbox.pl"
# PREFIX_URL = "https://api.allegro.pl"
TOKEN_URL = "https://allegro.pl.allegrosandbox.pl/auth/oauth/token"


class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send(fail_silently=False)

def get_access_token():
    try:
        data = {'grant_type': 'client_credentials'}
        access_token_response = requests.post(TOKEN_URL, data=data, verify=False,
                                              allow_redirects=False, auth=(CLIENT_ID, CLIENT_SECRET))
        tokens = json.loads(access_token_response.text)
        print(tokens)
        global ACCESS_TOKEN
        ACCESS_TOKEN = tokens['access_token']
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)


def get_search(search, id, token, flag = False):
    print("get search -> token: ", token)
    try:
        url = PREFIX_URL + "/offers/listing?phrase=" + search
        headers = {'Authorization': 'Bearer ' + token, 'Accept': "application/vnd.allegro.public.v1+json"}
        offer_result = requests.get(url, headers=headers, verify=False)

        js = json.dumps(offer_result.json(), indent=4)
        obj = json.loads(js)
        
        for i in obj['items']['promoted']:
            item = {'id': i['id'],
                    'name': i['name'],
                    'price': i['sellingMode']['price']['amount'],
                    'currency': i['sellingMode']['price']['currency']}

        filter_one = [x for x in obj['items']['promoted'] if x['id'] == id]
        # print(filter_one)
        return {'id': filter_one[0]['id'],
                'name': filter_one[0]['name'],
                'price': filter_one[0]['sellingMode']['price']['amount'],
                'currency': filter_one[0]['sellingMode']['price']['currency']}

    except:
        print("Error " +  str(flag))
        if flag==True:
            return {'id': 'not found',
                    'name': 'not found',
                    'price': 'not found',
                    'currency': 'not found'}
        else:
            get_access_token()
            return get_search(search, id, ACCESS_TOKEN, True)


def save_search_to_db(search, id, token):
    search = get_search(search, id, token)
    if search['id'] == 'not found':
        return {'error_message': 'Product not found'}
    else:
        price = float(search['price'])
        currency = search['currency']
        product = Product.objects.get(id=id)
        old_price = Price.objects.filter(product=product).order_by('-date').first()
        if (old_price is not None) and (abs(old_price.price - price) < 0.001):
            return {'error_message': 'Price not changed'}
        price_model = Price(product=product, price=price, currency=currency)
        price_model.save()

        # Send email if price is lower than target price
        if product.target_price is not None and price <= product.target_price:
            user = product.owner
            username = user.username
            email = user.email

            email_body = "Hi " + username + "!\n" \
                        + " The price of your product \"" + product.name + "\" is lower than your target price.\n" \
                        + " Current price: " + str(price) + " " + currency + ".\n\n" \
                        + " Best regards, Allegro Tracker."

            email_to_send = EmailMessage(
                'Allegro Tracker - Price alert',
                email_body,
                'noreplay@allegrotracker.com',
                [email],
            )
            EmailThread(email_to_send).start()
        return {'success_message': 'Product added'}


def run_continuously(self, interval=1):
    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                self.run_pending()
                time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.start()
    return cease_continuous_run


@login_required(login_url="/accounts/login")
def index(request):
    products = Product.objects.filter(owner=request.user)
    paginator = Paginator(products, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'products': products,
               'prices': Price.objects.all(),
               'page_obj': page_obj,
               }
    return render(request, "AllegroTracker/index.html", context)


@login_required(login_url="/accounts/login")
def add_product(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        p_id = request.POST.get('id')
        refresh_rate = request.POST.get('refresh_rate')
        description = request.POST.get('description')
        target_price = request.POST.get('target_price')
        if(float(target_price) <= 0):
            return render(request, 'AllegroTracker/add_product.html',
                          {'values': request.POST, 'error_message': 'Target price cannot be negative'})
        
        owner = request.user

        product = Product(name=name, id=p_id, owner=owner, description=description, target_price=target_price)

        if refresh_rate:
            refresh_rate = int(refresh_rate)
            if refresh_rate < 0:
                return render(request, 'AllegroTracker/add_product.html',
                              {'values': request.POST, 'error_message': 'Refresh rate cannot be negative'})
            else:
                product.minutes_refresh_rate = refresh_rate

        search = get_search(name, p_id, ACCESS_TOKEN)
        if search['id'] == 'not found':
            return render(request, 'AllegroTracker/add_product.html',
                          {'values': request.POST, 'error_message': 'Product not found'})

        else:
            product.save()
            save_search_to_db(name, p_id, ACCESS_TOKEN)
            scheduler = Scheduler()
            scheduler.every(product.minutes_refresh_rate).minutes.do(save_search_to_db, name, p_id, ACCESS_TOKEN)
            run_continuously(scheduler)

        return redirect('index')
    else:
        return render(request, 'AllegroTracker/add_product.html')


@login_required(login_url="/accounts/login")
def edit_product(request, product_id):
    product = Product.objects.get(id=product_id)
    context = {'product': product,
               'values': product,
               }
    if request.method == 'GET':
        return render(request, 'AllegroTracker/edit_product.html', context)
    else:
        name = request.POST.get('name')
        p_id = request.POST.get('id')
        refresh_rate = request.POST.get('refresh_rate')
        description = request.POST.get('description')

        if refresh_rate:
            refresh_rate = int(refresh_rate)
            if refresh_rate < 0:
                return render(request, 'AllegroTracker/edit_product.html',
                              {'values': request.POST, 'error_message': 'Refresh rate cannot be negative'})
            else:
                product.minutes_refresh_rate = refresh_rate

        search = get_search(name, p_id, ACCESS_TOKEN)
        if search['id'] == 'not found':
            return render(request, 'AllegroTracker/edit_product.html',
                          {'values': request.POST, 'error_message': 'Product not found'})

        else:
            product.name = name
            product.id = p_id
            product.description = description
            product.save()

            save_search_to_db(name, p_id, ACCESS_TOKEN)
            scheduler = Scheduler()
            scheduler.every(product.minutes_refresh_rate).minutes.do(save_search_to_db, name, p_id, ACCESS_TOKEN)
            run_continuously(scheduler)

        return redirect('index')


def delete_product(request, product_id):
    product = Product.objects.get(id=product_id)
    product.delete()
    return redirect('index')

def return_graph(prices):
    try:
        array2 = []
        for price in prices:
            array2.append({'Date': datetime.fromtimestamp(price.date.timestamp()), 'Close': price.price})

        df = pd.DataFrame(array2)

        start_date = pd.to_datetime('2023-04-01')
        end_date = pd.to_datetime('2023-12-31')
        new_df = (df['Date'] >= start_date) & (df['Date'] <= end_date)
        df1 = df.loc[new_df]
        stock_data = df1.set_index('Date')

        # Adjust figure size to accommodate the legend
        fig, ax = plt.subplots(figsize=(10, 6))

        ax.plot(stock_data.index, stock_data["Close"])

        # Use tight layout to automatically adjust spacing
        fig.tight_layout()

        imgdata = StringIO()
        plt.savefig(imgdata, format='svg')
        imgdata.seek(0)

        data = imgdata.getvalue()
    except:
        if prices is None or prices.count() == 0:
            data = 'No data to display'
        else:
            data = 'Could not load graph'
    return data

@login_required(login_url="/accounts/login")
def product_details(request, product_id):
    product = Product.objects.get(id=product_id)
    prices = Price.objects.filter(product=product)
    paginator = Paginator(prices, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'product': product,
               'prices': prices,
               'page_obj': page_obj,
               'graph': return_graph(prices),
               }
    return render(request, "AllegroTracker/product_details.html", context)


def search_product(request):
    if request.method == 'POST':
        search_string = json.loads(request.body).get('search_string', '')
        products = Product.objects.filter(name__icontains=search_string, owner=request.user)
        data = products.values()
        return JsonResponse(list(data), safe=False)


def register(request):
    if request.method == 'GET':
        return render(request, 'registration/register.html', {})

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        context = {
            'fieldValues': request.POST
        }

        is_error = False
        if not username.isalnum():
            messages.error(request, 'Username should only contain letters and numbers')
            is_error = True
        if not validate_email(email):
            messages.error(request, 'Please enter a valid email')
            is_error = True
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            is_error = True
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            is_error = True
        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters long')
            is_error = True
        if is_error:
            return render(request, 'registration/register.html', context)

        new_user = User.objects.create_user(username=username, email=email)
        new_user.set_password(password)
        new_user.is_active = False
        new_user.save()

        domain = get_current_site(request).domain
        link = reverse('activate', kwargs={'uidb64': urlsafe_base64_encode(force_bytes(new_user.pk)),
                                           'token': token_generation.make_token(new_user)})

        email_body = "Hi " + new_user.username + "!" \
                     + " Thank you for registering in Allegro Tracker.\n" \
                     + " Please use this link to verify your account:\n" \
                     + 'http://' + domain + link

        email_to_send = EmailMessage(
            'Allegro Tracker - Activate your account',
            email_body,
            'noreplay@allegrotracker.com',
            [email],
        )
        EmailThread(email_to_send).start()
        return HttpResponseRedirect(reverse('index', args=()))


class verification_view(View):
    def get(self, request, uidb64, token):
        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)

            if not token_generation.check_token(user, token):
                return redirect('login' + '?message=' + 'User already activated')

            if user.is_active:
                return redirect('login')
            user.is_active = True
            user.save()

        except Exception as e:
            pass
        return redirect('login')
