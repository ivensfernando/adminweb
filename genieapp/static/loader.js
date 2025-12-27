(function() {
    // Add loader HTML to the end of the body
    const loaderHTML = `
        <div id="custom-loader" style="display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0, 0, 0, 0.5); z-index: 9999; align-items: center; justify-content: center;">
            <svg width="50" height="50" viewBox="0 0 50 50" xmlns="http://www.w3.org/2000/svg" fill="#000000">
                <path opacity=".5" d="M0 25A25 25 0 1 0 50 25A25 25 0 1 0 0 25Z"></path>
                <path d="M50 25C50 38.81 38.81 50 25 50V0C38.81 0 50 11.19 50 25Z" transform="rotate(216 25 25)">
                    <animateTransform attributeName="transform" type="rotate" from="0 25 25" to="360 25 25" dur="1s" repeatCount="indefinite"></animateTransform>
                </path>
            </svg>
        </div>
    `;


    document.body.insertAdjacentHTML('beforeend', loaderHTML);

    // Function to show or hide the loader based on localStorage value
    function checkLoaderStatus() {
        const loader = document.getElementById('custom-loader');
        const isLoading = localStorage.getItem('loading');
        if (isLoading) {
            loader.style.display = 'flex'; // Show loader
        } else {
            loader.style.display = 'none'; // Hide loader
        }
    }

    // Check the loader status initially
    checkLoaderStatus();

    window.addEventListener('localStorageChange', (event) => {
        console.log("loader.js, addEventListener", event.key);
        checkLoaderStatus();
    });

})();
