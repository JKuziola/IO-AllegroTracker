const username = document.getElementById('usernameField');
const email = document.getElementById('emailField');
const password = document.getElementById('passwordField');
const username_feedback = document.querySelector('.username-invalid-feedback');
const email_feedback = document.querySelector('.email-invalid-feedback');
const submitBtn = document.querySelector("#submit-btn");
const password_toggle = document.querySelector(".show-password-toggle");
let isUsernameValid = false;
let isLoginValid = false;

const handleTogglePasswordClick = (e) => {
    if (password_toggle.textContent === "SHOW PASSWORD") {
        password_toggle.textContent = "HIDE PASSWORD";
        password.setAttribute("type", "text");
    } else {
        password_toggle.textContent = "SHOW PASSWORD";
        password.setAttribute("type", "password");
    }
}

password_toggle.addEventListener("click", handleTogglePasswordClick);
