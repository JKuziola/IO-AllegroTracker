const searchField = document.querySelector("#searchField");
const tableOutput = document.querySelector(".table-output");
const appTable = document.querySelector(".app-table");
const paginationContainer = document.querySelector(".pagination-container");
const tableBody = document.querySelector(".table-body");
const noResults = document.querySelector(".no-results");
tableOutput.style.display = "none";

searchField.addEventListener("keyup", (e) => {
    const searchValue = e.target.value;

    if (searchValue.trim().length > 0) {
        paginationContainer.style.display = "none";
        fetch("/AllegroTracker/search_product", {
            body: JSON.stringify({search_string: searchValue}),
            method: "POST",
        })
            .then((res) => res.json())
            .then((data) => {
                if (data.length === 0) {
                    appTable.style.display = "none";
                    tableOutput.style.display = "none";
                    noResults.style.display = "block";
                } else {
                    noResults.style.display = "none";
                    tableBody.innerHTML = "";
                    data.forEach((item) => {
                        tableBody.innerHTML += `
                    <tr>
                    <td>${item.id}</td>
                    <td>${item.name}</td>
                    <td>${item.date_added}</td> <!-- fix to date -->
                    <td><a href="/AllegroTracker/product_details/${item.id}">Details</a></td>
                    <td><a href="/AllegroTracker/edit_product/${item.id}">Edit</a></td>
                    <td><a href="/AllegroTracker/delete_product/${item.id}">Delete</a></td>
                    </tr>`;
                    });
                    appTable.style.display = "none";
                    tableOutput.style.display = "block";
                }
            });
    } else {
        tableOutput.style.display = "none";
        noResults.style.display = "none";
        appTable.style.display = "block";
        paginationContainer.style.display = "block";
    }
});
