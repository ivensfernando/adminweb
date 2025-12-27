document.getElementById('loginForm').addEventListener('submit', async function(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = {
        email: formData.get('email'),
        password: formData.get('password'),
    };
    try {
        const response = await fetch('/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });
        const responseData = await response.json();
        if (response.status === 200) {
            // Save the JWT token or use as needed.
            const token = responseData.token;
            console.log(token);
            localStorage.setItem('token', token);
            alert('Login successful.');
            window.location.href = '/auth/home';
        } else {
            alert('Login failed.');
            localStorage.removeItem('token');
        }
    } catch (error) {
        console.error('Error:', error);
    }
});
