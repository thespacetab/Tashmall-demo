// Функция для добавления товара в корзину
function addToCart(productId, name, price) {
	let cart = JSON.parse(localStorage.getItem('cart') || '[]')
	let item = cart.find(i => i.productId === productId)
	if (item) {
		item.qty += 1
	} else {
		cart.push({ productId, name, price, qty: 1 })
	}
	localStorage.setItem('cart', JSON.stringify(cart))
	showCart()
}

// Функция для удаления товара из корзины
function removeFromCart(productId) {
	let cart = JSON.parse(localStorage.getItem('cart') || '[]')
	cart = cart.filter(i => i.productId !== productId)
	localStorage.setItem('cart', JSON.stringify(cart))
	showCart()
}

// Функция отображения содержимого корзины
function showCart() {
	let cart = JSON.parse(localStorage.getItem('cart') || '[]')
	let cartDiv = document.getElementById('cart-list')
	let totalDiv = document.getElementById('cart-total')
	let buttonDiv = document.getElementById('cart-action') // <--- обязательно нужен этот div в html!
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

// Функция оформления заказа
function checkoutOrder() {
    let cart = JSON.parse(localStorage.getItem('cart') || '[]')
    if (!cart.length) {
        alert('Корзина пуста!')
        return
    }
    let user_id = localStorage.getItem('user_id') || prompt('Введите ваш Telegram user_id (или id покупателя):')
    if (!user_id) {
        alert('Необходимо ввести user_id!')
        return
    }
    let shop_id = localStorage.getItem('shop_id') || prompt('Введите shop_id магазина:')
    if (!shop_id) {
        alert('Необходимо ввести shop_id!')
        return
    }
    fetch('http://localhost:8000/api/orders', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            buyer_id: user_id,
            shop_id: shop_id,
            cart
        })
    })
    .then(res => {
        if (res.ok) return res.json()
        throw new Error('Ошибка оформления заказа')
    })
    .then(data => {
        alert('Заказ успешно оформлен!')
        localStorage.removeItem('cart')
        showCart()
    })
    .catch(err => {
        alert('Ошибка оформления заказа: ' + err.message)
    })
}

// Функция для отображения корзины при загрузке страницы
window.onload = function() {
	if (typeof showCart === 'function') showCart()
}
