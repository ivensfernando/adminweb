document.addEventListener('DOMContentLoaded', async () => {
    const token = localStorage.getItem('token');
    if (!token) {
        console.error('Token is not set!');
        return;
    }
    localStorage.setItem('loading', 'true');
    window.dispatchEvent(new Event('localStorageChange'));

    // Load the publishable key from the server. The publishable key
    // is set in your .env file.
    const {publishableKey} = await fetch('/api/pay/config', {
        method: "GET",
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json",
        },
    }).then((r) => r.json());
    if (!publishableKey) {
        addMessage(
            'No publishable key returned from the server. Please check `.env` and try again'
        );
        alert('Please set your Stripe publishable API key in the .env file');
    }

    const stripe = Stripe(publishableKey, {
        apiVersion: '2020-08-27',
    });

    const url = new URL(window.location);
    const clientSecret = url.searchParams.get('payment_intent_client_secret');

    const {error, paymentIntent} = await stripe.retrievePaymentIntent(
        clientSecret
    );
    if (error) {
        addMessage(error.message);
    }
    addMessage(`Payment ${paymentIntent.status}: ${paymentIntent.id}`);

    localStorage.removeItem('loading');
    window.dispatchEvent(new Event('localStorageChange'));

});
