if (localStorage.getItem('theme') === 'dark') {
    document.body.classList.add("dark-mode");
    document.getElementById("change-theme").innerHTML = "Light Mode";
}
else {
    document.body.classList.remove("dark-mode");
    document.getElementById("change-theme").innerHTML = "Dark Mode";
}

function changeTheme() {
    if (document.body.classList.contains("dark-mode")) {
        document.body.classList.remove("dark-mode");
        localStorage.setItem('theme', 'light');
    }
    else {
        document.body.classList.add("dark-mode");
        localStorage.setItem('theme', 'dark');
    }

    document.getElementById("change-theme").innerHTML = document.body.classList.contains("dark-mode") ? "Light Mode" : "Dark Mode";
}
