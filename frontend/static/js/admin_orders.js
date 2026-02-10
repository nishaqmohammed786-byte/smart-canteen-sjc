document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".status-btn").forEach(button => {
        button.addEventListener("click", function () {
            const orderId = this.dataset.id;
            const status = this.dataset.status;

            fetch("/admin/orders/update", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ order_id: orderId, status: status })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    const statusCell = document.getElementById("status-" + orderId);
                    statusCell.innerText = status;
                    statusCell.className = "status " + status.toLowerCase();

                    // Disable buttons
                    document.querySelectorAll(`button[data-id='${orderId}']`).forEach(btn => btn.disabled = true);

                    alert(data.message);
                } else {
                    alert("Failed: " + data.message);
                }
            })
            .catch(err => {
                console.error(err);
                alert("Something went wrong");
            });
        });
    });

    // Optional: Auto-refresh every 30s
    setInterval(() => location.reload(), 30000);
});
