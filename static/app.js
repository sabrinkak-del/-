// --- State ---
let menuData = { pizzas: [], toppings: [] };
let cart = [];
let modalPizzaId = null;
let modalQty = 1;

// --- DOM refs ---
const menuGrid = document.getElementById("menu-grid");
const cartSidebar = document.getElementById("cart-sidebar");
const cartOverlay = document.getElementById("cart-overlay");
const cartItemsEl = document.getElementById("cart-items");
const cartFooter = document.getElementById("cart-footer");
const cartCountEl = document.getElementById("cart-count");
const cartTotalEl = document.getElementById("cart-total");
const toppingsModal = document.getElementById("toppings-modal");
const orderSummary = document.getElementById("order-summary");

// --- Load menu ---
async function loadMenu() {
    try {
        const res = await fetch("/api/menu");
        menuData = await res.json();
        renderMenu();
    } catch {
        menuGrid.innerHTML = '<p style="text-align:center;color:#999">שגיאה בטעינת התפריט</p>';
    }
}

function renderMenu() {
    menuGrid.innerHTML = menuData.pizzas.map(pizza => `
        <div class="menu-card">
            <div class="menu-card-image">${pizza.image}</div>
            <div class="menu-card-body">
                <h3>${pizza.name}</h3>
                <p class="description">${pizza.description}</p>
                <div class="menu-card-footer">
                    <span class="price">₪${pizza.price}</span>
                    <button class="add-btn" onclick="openToppings(${pizza.id})">הוסף</button>
                </div>
            </div>
        </div>
    `).join("");
}

// --- Toppings Modal ---
function openToppings(pizzaId) {
    modalPizzaId = pizzaId;
    modalQty = 1;
    const pizza = menuData.pizzas.find(p => p.id === pizzaId);
    document.getElementById("modal-title").textContent = pizza.name;
    document.getElementById("modal-qty").textContent = "1";

    document.getElementById("toppings-list").innerHTML = menuData.toppings.map(t => `
        <div class="topping-item">
            <input type="checkbox" id="top-${t.id}" value="${t.id}">
            <label for="top-${t.id}">${t.name}</label>
            <span class="topping-price">+₪${t.price}</span>
        </div>
    `).join("");

    toppingsModal.style.display = "flex";
}

function closeModal() {
    toppingsModal.style.display = "none";
}

function changeQty(delta) {
    modalQty = Math.max(1, modalQty + delta);
    document.getElementById("modal-qty").textContent = modalQty;
}

function confirmAdd() {
    const selectedToppings = [];
    menuData.toppings.forEach(t => {
        if (document.getElementById(`top-${t.id}`).checked) {
            selectedToppings.push(t.id);
        }
    });

    cart.push({
        pizza_id: modalPizzaId,
        quantity: modalQty,
        toppings: selectedToppings,
    });

    closeModal();
    updateCart();
}

// --- Cart ---
function toggleCart() {
    cartSidebar.classList.toggle("open");
    cartOverlay.classList.toggle("open");
}

function toggleNav() {
    document.querySelector(".nav-links").classList.toggle("open");
}

function updateCart() {
    const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
    cartCountEl.textContent = totalItems;

    if (cart.length === 0) {
        cartItemsEl.innerHTML = '<p class="cart-empty">העגלה ריקה</p>';
        cartFooter.style.display = "none";
        orderSummary.innerHTML = "";
        return;
    }

    let total = 0;
    cartItemsEl.innerHTML = cart.map((item, i) => {
        const pizza = menuData.pizzas.find(p => p.id === item.pizza_id);
        let itemPrice = pizza.price * item.quantity;
        const toppingNames = [];
        item.toppings.forEach(tid => {
            const t = menuData.toppings.find(t => t.id === tid);
            if (t) {
                itemPrice += t.price * item.quantity;
                toppingNames.push(t.name);
            }
        });
        total += itemPrice;
        const extras = toppingNames.length ? toppingNames.join(", ") : "";
        return `
            <div class="cart-item">
                <div class="cart-item-info">
                    <h4>${pizza.name} × ${item.quantity}</h4>
                    ${extras ? `<p>${extras}</p>` : ""}
                </div>
                <div class="cart-item-actions">
                    <span class="cart-item-price">₪${itemPrice}</span>
                    <button class="remove-btn" onclick="removeFromCart(${i})">✕</button>
                </div>
            </div>
        `;
    }).join("");

    cartTotalEl.textContent = total;
    cartFooter.style.display = "block";

    // Update order summary section
    orderSummary.innerHTML = cart.map((item) => {
        const pizza = menuData.pizzas.find(p => p.id === item.pizza_id);
        let itemPrice = pizza.price * item.quantity;
        item.toppings.forEach(tid => {
            const t = menuData.toppings.find(t => t.id === tid);
            if (t) itemPrice += t.price * item.quantity;
        });
        return `<div class="summary-item"><span>${pizza.name} × ${item.quantity}</span><span>₪${itemPrice}</span></div>`;
    }).join("") + `<div class="summary-total"><span>סה"כ</span><span>₪${total}</span></div>`;
}

function removeFromCart(index) {
    cart.splice(index, 1);
    updateCart();
}

// --- Order Submission ---
async function submitOrder(e) {
    e.preventDefault();

    if (cart.length === 0) {
        alert("העגלה ריקה! הוסיפו פיצות לפני ביצוע הזמנה.");
        return;
    }

    const btn = document.getElementById("submit-btn");
    btn.disabled = true;
    btn.textContent = "שולח...";

    const order = {
        name: document.getElementById("order-name").value,
        phone: document.getElementById("order-phone").value,
        address: document.getElementById("order-address").value,
        notes: document.getElementById("order-notes").value,
        items: cart,
    };

    try {
        const res = await fetch("/api/order", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(order),
        });
        const data = await res.json();

        if (data.success) {
            document.getElementById("order-form").style.display = "none";
            orderSummary.style.display = "none";
            const conf = document.getElementById("order-confirmation");
            conf.style.display = "block";
            conf.innerHTML = `
                <h3>✅ ההזמנה התקבלה!</h3>
                <p>מספר הזמנה: <strong>${data.order_id}</strong></p>
                <p>סה"כ לתשלום: <strong>₪${data.total}</strong></p>
                <p>ההזמנה בדרך אליכם! 🛵</p>
            `;
            cart = [];
            updateCart();
        } else {
            alert("שגיאה: " + data.error);
        }
    } catch {
        alert("שגיאה בשליחת ההזמנה. נסו שוב.");
    } finally {
        btn.disabled = false;
        btn.textContent = "שלח הזמנה";
    }
}

// --- Init ---
loadMenu();
