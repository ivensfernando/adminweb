function jwtDecode(token) {
    function base64UrlDecode(str) {
        str = str.replace(/-/g, '+').replace(/_/g, '/');
        while (str.length % 4) {
            str += '=';
        }
        return decodeURIComponent(atob(str).split('').map(function(c) {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));
    }

    const parts = token.split('.');
    if (parts.length !== 3) {
        throw new Error('JWT token has wrong number of parts.');
    }

    const payload = JSON.parse(base64UrlDecode(parts[1]));

    return payload;
}


document.addEventListener('DOMContentLoaded', async () => {
    const token = localStorage.getItem('token');
    if (!token) {
        console.error('Token is not set!');
        window.location.href = "/auth/login";
        return;
    }
    localStorage.setItem('loading', 'true');
    window.dispatchEvent(new Event('localStorageChange'));

    const decodedToken = jwtDecode(token);
    console.log("decodedToken, ", decodedToken)

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

    // On page load, we create a PaymentIntent on the server so that we have its clientSecret to
    // initialize the instance of Elements below. The PaymentIntent settings configure which payment
    // method types to display in the PaymentElement.
    const {
        error: backendError,
        clientSecret
    } = await fetch('/api/pay/create-payment-intent?plan_id=1', {
        method: "GET",
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json",
        },
    }).then(r => r.json());
    if (backendError) {
        addMessage(backendError.message);
    }
    addMessage(`Client secret returned. User: `+decodedToken.username);

    // Initialize Stripe Elements with the PaymentIntent's clientSecret,
    // then mount the payment element.
    const elements = stripe.elements({clientSecret});
    const paymentElement = elements.create('payment');
    paymentElement.mount('#payment-element');
    // Create and mount the linkAuthentication Element to enable autofilling customer payment details
    const linkAuthenticationElement = elements.create("linkAuthentication");
    linkAuthenticationElement.mount("#link-authentication-element");


    // If the customer's email is known when the page is loaded, you can
    // pass the email to the linkAuthenticationElement on mount:
    //
    // linkAuthenticationElement.mount("#link-authentication-element",  {
    //     defaultValues: {
    //       email: decodedToken.username,
    //     }
    // })
    // If you need access to the email address entered:
    //
    // Ensure element is fully loaded
    linkAuthenticationElement.on('ready', function() {
        localStorage.removeItem('loading');
        window.dispatchEvent(new Event('localStorageChange'));

        // Assuming the linkAuthenticationElement is created somewhere above this code
        const token = localStorage.getItem('token');
        if (!token) {
            console.error('Token is not set!');
            return;
        }

        const decodedToken = jwtDecode(token);
        console.log("linkAuthenticationElement, ready, ", decodedToken)
        linkAuthenticationElement.update({
            defaultValues: {
                    email: decodedToken.username,
            },
        });
        // linkAuthenticationElement.update({business: {email: decodedToken.username}});

    });
     linkAuthenticationElement.on('change', (event) => {
       const email = event.value.email;
       console.log("linkAuthenticationElement, ",{ email });
     })

    // When the form is submitted...
    const form = document.getElementById('payment-form');
    let submitted = false;
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        // Disable double submission of the form
        if (submitted) {
            return;
        }
        submitted = true;
        form.querySelector('button').disabled = true;

        const nameInput = document.querySelector('#name');

        // Confirm the payment given the clientSecret
        // from the payment intent that was just created on
        // the server.
        const {error: stripeError} = await stripe.confirmPayment({
            elements,
            confirmParams: {
                return_url: `${window.location.origin}/api/pay/return`,
            }
        });

        if (stripeError) {
            addMessage(stripeError.message);

            // reenable the form.
            submitted = false;
            form.querySelector('button').disabled = false;
            return;
        }
    });
});
