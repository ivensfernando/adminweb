document.addEventListener("DOMContentLoaded", function () {
    fetchData();
});

function fetchData() {
    const token = localStorage.getItem('token');
    if (!token) {
        console.error('Token is not set!');
        window.location.href = "/auth/login";
        return;
    }

    localStorage.setItem('loading', 'true');
    window.dispatchEvent(new Event('localStorageChange'));

    fetch("/api/account_api_key", {
        method: "GET",
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json",
        },
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // document.getElementById("keyID").innerText = data.id;
        // document.getElementById("keyHash").innerText = data.key_hash;
        document.getElementById("keyUnsafe").innerText = data.key_unsafe;
        document.getElementById("usageLimit").innerText = data.usage_limit;
        document.getElementById("usageCount").innerText = data.usage_count;
        // document.getElementById("genieUsersID").innerText = data.genie_users_id;
        // document.getElementById("allowedPaths").innerText = data.allowed_paths;

        localStorage.removeItem('loading');
        window.dispatchEvent(new Event('localStorageChange'));
    })
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error.message);
        localStorage.removeItem('loading');
        window.dispatchEvent(new Event('localStorageChange'));
    });
}
