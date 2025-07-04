// ======= Tashmall WebApp (обновлено для заказов) =======

const API_URL = "http://localhost:8000/api";

// ======= Корзина =======
function addToCart(productId, name, price, shopId) {
	let cart = JSON.parse(localStorage.getItem('cart') || '[]')
	let found = cart.find(item => item.productId === productId)
	if (found) {
		found.qty += 1
	} else {
		cart.push({ productId, name, price, qty: 1, shopId })
	}
	localStorage.setItem('cart', JSON.stringify(cart))
	alert('Товар добавлен в корзину!')
}

function removeFromCart(productId) {
	let cart = JSON.parse(localStorage.getItem('cart') || '[]')
	cart = cart.filter(item => item.productId !== productId)
	localStorage.setItem('cart', JSON.stringify(cart))
	showCart()
}

function showCart() {
	let cart = JSON.parse(localStorage.getItem('cart') || '[]')
	let cartDiv = document.getElementById('cart-list')
	let totalDiv = document.getElementById('cart-total')
	let buttonDiv = document.getElementById('cart-action')
	cartDiv.innerHTML = ''
	let total = 0
	cart.forEach(item => {
		total += item.price * item.qty
		let el = document.createElement('div')
		el.innerHTML = `${item.name} — ${item.qty} шт × ${item.price}₸ <button onclick="removeFromCart(${item.productId})">Удалить</button>`
		cartDiv.appendChild(el)
	})
	totalDiv.innerHTML = `<h3>Итого: ${total}₸</h3>`
	if (cart.length > 0) {
		buttonDiv.innerHTML = `<button onclick="checkoutOrder()">Оформить заказ</button>`
	} else {
		buttonDiv.innerHTML = ''
	}
}

// ======= Оформление заказа =======
function checkoutOrder() {
	let cart = JSON.parse(localStorage.getItem('cart') || '[]')
	if (!cart.length) {
		alert("Корзина пуста")
		return
	}
	let shop_id = cart[0].shopId
	// Для демо — спросим user_id вручную, в реальном проекте получить из Telegram WebApp API!
	let buyer_id = window.tgUserId || prompt("Введите ваш user_id (Telegram):")
	const items = cart.map(item => ({
		product_id: item.productId,
		qty: item.qty,
		price_snapshot: item.price
	}))
	fetch(`${API_URL}/orders`, {
		method: "POST",
		headers: {"Content-Type": "application/json"},
		body: JSON.stringify({buyer_id: buyer_id, shop_id: shop_id, items: items})
	})
	.then(res => res.json())
	.then(data => {
		if (data.success) {
			localStorage.removeItem('cart')
			alert('Заказ успешно оформлен!')
			showCart()
			showMyOrders(buyer_id)
		} else {
			alert('Ошибка оформления заказа')
		}
	})
}

// ======= Отображение заказов пользователя =======
function showMyOrders(user_id) {
	fetch(`${API_URL}/orders/${user_id}`)
	.then(res => res.json())
	.then(orders => {
		let el = document.getElementById("myorders")
		if (!el) return
		if (!orders.length) {
			el.innerHTML = "<i>У вас нет заказов</i>"
			return
		}
		let html = ""
		for (let o of orders) {
			let order = o.order
			html += `<div style="border:1px solid #888;margin:8px;padding:8px;">
				<b>Заказ №${order.id}</b><br>
				Статус: ${order.status}<br>
				Дата: ${order.created_at}<br>
				<ul>`
			for (let it of o.items) {
				html += `<li>${it.name} — ${it.qty} x ${it.price_snapshot}</li>`
			}
			html += "</ul></div>"
		}
		el.innerHTML = html
	})
}

// ======= Загрузка товаров (пример) =======
function loadProducts(shopId) {
	fetch(`${API_URL}/products/${shopId}`)
	.then(res => res.json())
	.then(products => {
		let productsEl = document.getElementById("products")
		if (!productsEl) return
		let html = ""
		for (let p of products) {
			html += `<div style="border:1px solid #ccc;margin:8px;padding:8px;">
				<b>${p.name}</b><br>
				<img src="${API_URL}/photo_telegram/${p.photo_file_id}" style="max-width:120px"><br>
				Цена: ${p.price}<br>
				<button onclick='addToCart(${p.id}, "${p.name}", ${p.price}, ${p.shop_id})'>В корзину</button>
			</div>`
		}
		productsEl.innerHTML = html
	})
}

// ======= Инициализация =======
window.onload = function() {
	showCart()
	let user_id = window.tgUserId || 1 // или получить user_id из Telegram WebApp
	showMyOrders(user_id)
}
