import time
import traceback

from django.http import JsonResponse
from ninja import Router, Query
from django.http import HttpResponse

import stripe
import json

from config.settings.base import STRIPE_SECRET_KEY, STRIPE_PUBLISHABLE_KEY, STRIPE_WEBHOOK_SECRET, \
    STRIPE_TRIAL_PERIOD_DAYS
from src.db.api_helpers import create_or_update_user_keys
from src.db.history import get_chat_history_list_by_company_id
from src.db.login_helpers import getConn, get_user_by_id
from src.db.stripe_helpers import get_genie_payment_plan, insert_or_update_genie_users_payments, \
    get_genie_payment_history, update_status_genie_users_payments_by_subscription_id, \
    insert_or_update_genie_users_payments_by_subscription_id, \
    get_stripe_subscription
from src.utils.pdf import create_pdf

stripe_router = Router(tags=['Stripe'])

# For sample support and debugging, not required for production:
stripe.set_app_info(
    'biidinwebapi',
    version='0.0.1',
    url='https://wapi.biidin.com')

stripe.api_version = '2020-08-27'

stripe.api_key = STRIPE_SECRET_KEY

provider = "stripe"


@stripe_router.get('/pay')
def get_root(request):
    # You need to return a HttpResponse with the rendered template.
    from django.shortcuts import render
    return render(request, 'pay.html')


@stripe_router.get('/pay/return')
def get_root(request):
    # You need to return a HttpResponse with the rendered template.
    from django.shortcuts import render
    return render(request, 'return.html')


@stripe_router.get("/pay/config")
def get_config(request):
    prices = []
    prices_obj = stripe.Price.list(
        lookup_keys=['sample_basic', 'sample_premium', "metered"]
    )
    if prices_obj is not None:
        prices = prices_obj["data"]
    return {
        'publishableKey': STRIPE_PUBLISHABLE_KEY,
        'prices': prices,
        "STRIPE_TRIAL_PERIOD_DAYS": STRIPE_TRIAL_PERIOD_DAYS,
    }


@stripe_router.get("/pay/create-payment-intent")
def create_payment(
        request,
        plan_id: str = Query("e", description="Folder")
):
    token_data = request.auth
    print(f"create_payment, token_data={token_data}")

    user_id = token_data["user_id"]
    company_id = token_data["company_id"]

    print(f"create_payment, user_id={user_id}, plan_id={plan_id}, company_id={company_id}")

    try:
        plan = get_genie_payment_plan(getConn(), plan_id)
        print(f"create_payment, plan={plan}")

        if plan is None:
            print(f"create_payment, user_id={user_id}, failed to find a valid plan for user.")
            return JsonResponse({'error': {'message': "invalid_plan"}}, status=401)

        intent = stripe.PaymentIntent.create(
            amount=int(plan["amount"]),
            currency='USD',
            automatic_payment_methods={'enabled': True},
        )

        payment_intent = intent.id
        client_secret = intent.client_secret
        insert_or_update_genie_users_payments(getConn(), user_id, plan_id, payment_intent, client_secret, provider,
                                              "intent", company_id)

        print(f"create_payment, intent={intent}")

        return {'clientSecret': intent.client_secret}
    except stripe.error.StripeError as e:
        print(f"create_payment, StripeError, e={e}")
        return JsonResponse({'error': {'message': str(e)}}, status=400)
    except Exception as e:
        print(f"create_payment, Exception, e={e}")
        return JsonResponse({'error': {'message': str(e)}}, status=400)


@stripe_router.get("/pay/create-subscription")
def create_subscription(
        request,
        plan_id: str = Query(None, description="Folder"),
        coupon_code: str = Query(None, description="Folder"),
):
    token_data = request.auth
    print(f"create_subscription, token_data={token_data}")

    user_id = token_data["user_id"]
    company_id = token_data["company_id"]

    stripe_customer_id = token_data["stripe_customer_id"]
    print(f"create_subscription, user_id={user_id}, plan_id={plan_id}, stripe_customer_id={stripe_customer_id}")

    try:
        plan = get_genie_payment_plan(getConn(), plan_id)
        print(f"create_subscription, plan={plan}")

        if plan is None:
            print(f"create_subscription, user_id={user_id}, failed to find a valid plan for user.")
            return JsonResponse({'error': {'message': "invalid_plan"}}, status=401)

        # Create a SetupIntent to save the payment method
        setup_intent = stripe.SetupIntent.create(
            customer=stripe_customer_id
        )
        # print(f"create_subscription, setup_intent={setup_intent}")

        client_secret = setup_intent.client_secret
        status = "trial"
        if coupon_code:
            status = "coupon"
            promotion_code = stripe.PromotionCode.list(code=coupon_code).data[0]
            # Extract the coupon ID from the promotion code object
            coupon_id = promotion_code.coupon
            # Create the subscription with discount

            subscription = stripe.Subscription.create(
                customer=stripe_customer_id,
                items=[{
                    'price': plan_id,
                }],
                payment_behavior='default_incomplete',
                expand=['latest_invoice.payment_intent', "items"],
                coupon=coupon_id,
                # trial_end=trial_end
            )
        else:
            trial_end = int(time.time()) + STRIPE_TRIAL_PERIOD_DAYS * 24 * 60 * 60
            print(f"create_subscription, trial_end={trial_end}")

            # Create the subscription without discount
            subscription = stripe.Subscription.create(
                customer=stripe_customer_id,
                items=[{
                    'price': plan_id,
                }],
                payment_behavior='default_incomplete',
                expand=['latest_invoice.payment_intent'],
                trial_end=trial_end
            )

        subscription_id = subscription["id"]

        # print(f"create_subscription, subscription={subscription}")

        # payment_intent = subscription.latest_invoice.payment_intent.id
        # client_secret = subscription.latest_invoice.payment_intent.client_secret

        retrieved_subscription = stripe.Subscription.retrieve(subscription_id)
        print(f"create_subscription, retrieved_subscription={retrieved_subscription}")
        subscription_item_id = ""

        if retrieved_subscription and retrieved_subscription.items and retrieved_subscription['items']['data']:
            subscription_item_id = retrieved_subscription['items']['data'][0]['id']

        insert_or_update_genie_users_payments_by_subscription_id(
            conn=getConn(),
            genie_users_id=user_id,
            genie_payment_plan_id=plan["id"],
            subscription_id=subscription_id,
            client_secret=client_secret,
            provider=provider,
            status=status,
            company_id=company_id,
            subscription_item_id=subscription_item_id,
        )

        return {
            'clientSecret': client_secret,
            "subscription_id": subscription.id,
        }
    except stripe.error.StripeError as e:
        print(f"create_subscription, StripeError, e={e}")
        return JsonResponse({'error': {'message': str(e)}}, status=400)
    except Exception as e:
        traceback.print_exc()
        print(f"create_subscription, Exception, e={e}")
        return JsonResponse({'error': {'message': str(e)}}, status=400)


@stripe_router.post('/pay/update-subscription')
def update_subscription(
        request
):
    return JsonResponse({'error': {'message': "update_subscription is temp disabled"}}, status=401)

    token_data = request.auth
    print(f"update_subscription, token_data={token_data}")

    user_id = token_data["user_id"]
    stripe_customer_id = token_data["stripe_customer_id"]
    request_data = json.loads(request.body)
    subscription_id = request_data['subscription_id']

    print(
        f"update_subscription, user_id={user_id}, stripe_customer_id={stripe_customer_id}, subscription_id={subscription_id}")

    try:
        coupon = stripe.Coupon.create(
            percent_off=100,
            duration='once',
            max_redemptions=1
        )

        subscription = stripe.Subscription.modify(
            subscription_id,
            coupon=coupon
        )
        print(f"update_subscription, subscription={subscription}")

        return JsonResponse({'subscription': subscription}, status=200)
    except stripe.error.StripeError as e:
        print(f"update_subscription, StripeError, e={e}")
        return JsonResponse({'error': {'message': str(e)}}, status=400)
    except Exception as e:
        print(f"update_subscription, Exception, e={e}")
        return JsonResponse({'error': {'message': str(e)}}, status=400)


@stripe_router.post('/pay/apply-discount')
def apply_discount(
        request
):
    token_data = request.auth
    print(f"apply_discount, token_data={token_data}")

    user_id = token_data["user_id"]
    stripe_customer_id = token_data["stripe_customer_id"]
    request_data = json.loads(request.body)
    subscription_id = request_data['subscription_id']
    coupon_code = request_data['coupon_code']

    print(
        f"apply_discount, user_id={user_id}, stripe_customer_id={stripe_customer_id}, subscription_id={subscription_id}, coupon_code={coupon_code}")

    try:

        promotion_code = stripe.PromotionCode.list(code=coupon_code).data[0]
        # Extract the coupon ID from the promotion code object
        coupon_id = promotion_code.coupon

        subscription = stripe.Subscription.modify(
            subscription_id,
            coupon=coupon_id
        )
        print(f"apply_discount, subscription={subscription}")

        return JsonResponse({'subscription': subscription}, status=200)
    except stripe.error.StripeError as e:
        print(f"apply_discount, StripeError, e={e}")
        return JsonResponse({'error': {'message': str(e)}}, status=400)
    except Exception as e:
        print(f"apply_discount, Exception, e={e}")
        return JsonResponse({'error': {'message': str(e)}}, status=400)


@stripe_router.get("/pay/subscriptions")
def list_subscriptions(request):
    token_data = request.auth
    print(f"list_subscriptions, token_data={token_data}")

    stripe_customer_id = token_data["stripe_customer_id"]

    try:
        subscriptions = []
        trialing_subscriptions = []
        # Retrieve all subscriptions for given customer
        subscriptions_obj = stripe.Subscription.list(
            customer=stripe_customer_id,
            status='active',
            expand=['data.default_payment_method']
        )
        if subscriptions_obj is not None:
            subscriptions = subscriptions_obj["data"]

        trialing_subscriptions_obj = stripe.Subscription.list(
            customer=stripe_customer_id,
            status='trialing',
            expand=['data.default_payment_method']
        )
        if trialing_subscriptions_obj is not None:
            trialing_subscriptions = trialing_subscriptions_obj["data"]

        combined_subscriptions = subscriptions + trialing_subscriptions

        return JsonResponse({'subscriptions': combined_subscriptions}, status=200)
    except Exception as e:
        return JsonResponse({'error': {'message': str(e)}}, status=400)


@stripe_router.post('/pay/cancel-subscription')
def cancel_subscription(request):
    token_data = request.auth
    print(f"cancel_subscription, token_data={token_data}")

    user_id = token_data["user_id"]
    stripe_customer_id = token_data["stripe_customer_id"]

    request_data = json.loads(request.body)
    subscription_id = request_data['subscription_id']

    print(
        f"cancel_subscription, user_id={user_id}, stripe_customer_id={stripe_customer_id}, subscription_id={subscription_id}")

    try:
        # Cancel the subscription by deleting it
        deleted_subscription = stripe.Subscription.delete(subscription_id)
        return JsonResponse({'subscription': deleted_subscription}, status=200)
    except Exception as e:
        return JsonResponse({'error': {'message': str(e)}}, status=400)


@stripe_router.post("/pay/webhook")
def webhook_received(request):
    request_data = json.loads(request.body)

    if STRIPE_WEBHOOK_SECRET:
        print(f"webhook_received, STRIPE_WEBHOOK_SECRET")

        signature = request.headers.get('stripe-signature')
        try:
            event = stripe.Webhook.construct_event(
                payload=request.body, sig_header=signature, secret=STRIPE_WEBHOOK_SECRET
            )
            data = event['data']
        except Exception as e:
            print(f"webhook_received, error={e}")
            return JsonResponse({'error': {'message': str(e)}}, status=400)

        event_type = event['type']
    else:
        print(f"webhook_received, else")
        data = request_data['data']
        event_type = request_data['type']

    data_object = data['object']
    print(f"webhook_received, data_object={data_object}")
    # payment_intent_id = data_object["id"]
    status = "paid"
    subscription_id = data_object['subscription']

    if event_type == 'invoice.payment_succeeded':
        print(f'💰 Payment received!, subscription_id={subscription_id}')

        stripe_subscription_data = get_stripe_subscription(subscription_id)

        subscription_start_date = stripe_subscription_data["subscription_start_date"]
        subscription_status = stripe_subscription_data["subscription_status"]
        subscription_current_period_start_date = stripe_subscription_data["subscription_current_period_start_date"]
        subscription_current_period_end_date = stripe_subscription_data["subscription_current_period_end_date"]

        genie_users_id = update_status_genie_users_payments_by_subscription_id(
            conn=getConn(),
            subscription_id=subscription_id,
            status=status,
            subscription_start_date=subscription_start_date,
            subscription_status=subscription_status,
            subscription_current_period_start_date=subscription_current_period_start_date,
            subscription_current_period_end_date=subscription_current_period_end_date,
        )

        user = get_user_by_id(conn=getConn(), id=genie_users_id)
        if user is None:
            print(f"webhook_received, get_user_by_id, user not found genie_users_id={genie_users_id}")
            return JsonResponse({'error': {'message': "failed to find user"}}, status=400)

        company_id = user["company_id"]
        print(f"webhook_received, create_or_update_user_keys, genie_users_id={genie_users_id}, company_id={company_id}")
        create_or_update_user_keys(
            conn=getConn(),
            genie_users_id=genie_users_id,
            company_id=company_id
        )

        # Handle the customer.subscription.updated event
    if event_type == 'customer.subscription.updated':
        print(f'💰Subscription updated!, subscription_id={subscription_id}')

        previous_subscription = data['previous_attributes']

        # Check for plan change
        if 'items' in previous_subscription:
            previous_items = previous_subscription['items']
            current_items = data_object['items']
            if previous_items['data'][0]['price']['id'] != current_items['data'][0]['price']['id']:
                print('Subscription plan changed')
                # TODO: update subscription ?

        # Check for cancellation
        if 'cancel_at_period_end' in previous_subscription:
            if data_object['cancel_at_period_end']:
                print('Subscription set to cancel at period end')
                # TODO: cancel subscription

    # elif event_type == 'payment_intent.succeeded':
    #
    #     print(f'💰 Payment received!, payment_intent_id={payment_intent_id}')
    #     genie_users_id = update_status_genie_users_payments(conn=getConn(), payment_intent=payment_intent_id,
    #                                                         status=status)
    #
    #     user = get_user_by_id(conn=getConn(), id=genie_users_id)
    #     if user is None:
    #         print(f"webhook_received, get_user_by_id, user not found genie_users_id={genie_users_id}")
    #         return JsonResponse({'error': {'message': "failed to find user"}}, status=400)
    #
    #     company_id = user["company_id"]
    #     print(f"webhook_received, create_or_update_user_keys, genie_users_id={genie_users_id}, company_id={company_id}")
    #     create_or_update_user_keys(conn=getConn(), genie_users_id=genie_users_id, company_id=company_id)
    #
    # elif event_type == 'payment_intent.payment_failed':
    #     print(f'❌ Payment failed., payment_intent_id={payment_intent_id}')
    #     status = "payment_failed"
    #     genie_users_id = update_status_genie_users_payments(conn=getConn(), payment_intent=payment_intent_id,
    #                                                         status=status)
    #     # create_or_update_user_keys(conn=getConn(), genie_users_id=genie_users_id)

    else:
        print(f'❌ Payment, event_type={event_type} not recognized. ')

    return {'status': 'success'}


@stripe_router.get("/pay/payment_history")
def get_payment_history(request):
    token_data = request.auth
    print(f"get_payment_history, token_data={token_data}")

    user_id = token_data["user_id"]
    print(f"get_payment_history, user_id={user_id}")

    genie_users_payments = get_genie_payment_history(
        getConn(),
        user_id,
    )
    return 200, genie_users_payments


@stripe_router.get("/pay/get_usage_pdf")
def get_usage_pdf(
        request,
        year: int = Query(None, description="year"),
        month: int = Query(None, description="month"),
):
    token_data = request.auth
    print(f"get_usage_pdf, token_data={token_data}")

    user_id = token_data["user_id"]
    company_id = token_data["company_id"]
    print(f"get_usage_pdf, user_id={user_id}, company_id={company_id},")

    chat_history_list = get_chat_history_list_by_company_id(
        conn=getConn(),
        company_id=company_id,
        year=year,
        month=month,
    )

    pdf = create_pdf(data_list=chat_history_list)

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'

    return response
