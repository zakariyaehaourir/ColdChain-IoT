const searchInput = document.querySelector("#sensor-search");
const historyRows = document.querySelectorAll(".history-row");
const noSearchResults = document.querySelector("#no-search-results");

if (searchInput && historyRows.length && noSearchResults) {
    searchInput.addEventListener("input", () => {
        const searchTerm = searchInput.value.trim().toLocaleLowerCase();
        let visibleRows = 0;

        historyRows.forEach((row) => {
            const matches = row.textContent.toLocaleLowerCase().includes(searchTerm);
            row.hidden = !matches;
            if (matches) visibleRows += 1;
        });

        noSearchResults.hidden = visibleRows > 0;
    });
}

const latestAge = document.querySelector("#latest-age");

if (latestAge) {
    const receivedAt = new Date(latestAge.dateTime);

    if (!Number.isNaN(receivedAt.getTime())) {
        const formatAge = () => {
            const seconds = Math.max(0, Math.floor((Date.now() - receivedAt.getTime()) / 1000));
            let age;

            if (seconds < 60) {
                age = seconds <= 1 ? "quelques secondes" : `${seconds} s`;
            } else if (seconds < 3600) {
                const minutes = Math.floor(seconds / 60);
                const remainingSeconds = seconds % 60;
                age = `${minutes} min${remainingSeconds ? ` ${remainingSeconds} s` : ""}`;
            } else if (seconds < 86400) {
                const hours = Math.floor(seconds / 3600);
                const remainingMinutes = Math.floor((seconds % 3600) / 60);
                age = `${hours} h${remainingMinutes ? ` ${remainingMinutes} min` : ""}`;
            } else {
                const days = Math.floor(seconds / 86400);
                age = `${days} jour${days > 1 ? "s" : ""}`;
            }

            latestAge.textContent = `Il y a ${age}`;
        };

        formatAge();
        window.setInterval(formatAge, 1000);
    }
}
