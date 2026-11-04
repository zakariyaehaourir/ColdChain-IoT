const searchInput = document.querySelector("#sensor-search");
const sensorRows = document.querySelectorAll(".sensor-row");
const noSearchResults = document.querySelector("#no-search-results");

if (searchInput && sensorRows.length && noSearchResults) {
    searchInput.addEventListener("input", () => {
        const searchTerm = searchInput.value.trim().toLocaleLowerCase();
        let visibleRows = 0;

        sensorRows.forEach((row) => {
            const matches = row.textContent.toLocaleLowerCase().includes(searchTerm);
            row.hidden = !matches;
            if (matches) visibleRows += 1;
        });

        noSearchResults.hidden = visibleRows > 0;
    });
}
