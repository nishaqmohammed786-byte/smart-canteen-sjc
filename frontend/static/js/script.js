// Backend API base URL
const API_BASE = "http://127.0.0.1:5000";


/* ---------- LOAD MENU ---------- */
function loadMenu() {
    fetch(`${API_BASE}/menu`)
        .then(res => res.json())
        .then(data => {
            const menuDiv = document.getElementById("menu");
            menuDiv.innerHTML = "";

            data.menu.forEach(item => {
                const card = document.createElement("div");
                card.className = "menu-card";
                card.innerHTML = `
                    <img src="/static/images/${item.image}" 
                         alt="${item.item_name}" 
                         style="width:100%; border-radius:10px; margin-bottom:10px;">
                    <h3>${item.item_name}</h3>
                    <p>₹${item.price}</p>
                    <button class="btn" onclick="orderItem(${item.id})">
                        Order
                    </button>
                `;
                menuDiv.appendChild(card);
            });
        })
        .catch(err => console.error("Menu error:", err));
}

/* ---------- ORDER ITEM ---------- */
function orderItem(menuId) {
    const token = localStorage.getItem("token");
    if (!token) {
        alert("Please login to place an order.");
        window.location.href = "/login";
        return;
    }

    fetch(`${API_BASE}/order`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ menu_id: menuId })
    })
    .then(res => res.json())
    .then(data => alert(data.message))
    .catch(err => console.error("Order error:", err));
}
