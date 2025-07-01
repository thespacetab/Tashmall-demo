// Корзина — localStorage
function addToCart(productId, name, price) {
	let cart = JSON.parse(localStorage.getItem('cart') || '[]')
	let found = cart.find(item => item.productId === productId)
	if (found) {
		found.qty += 1
	} else {
		cart.push({ productId, name, price, qty: 1 })
	}
	localStorage.setItem('cart', JSON.stringify(cart))
	alert('Товар добавлен в корзину!')
}

function showCart() {
	let cart = JSON.parse(localStorage.getItem('cart') || '[]')
	let cartDiv = document.getElementById('cart-list')
	let totalDiv = document.getElementById('cart-total')
	cartDiv.innerHTML = ''
	let total = 0
	cart.forEach(item => {
		total += item.price * item.qty
		let el = document.createElement('div')
		el.innerHTML = `${item.name} — ${item.qty} шт × ${item.price}₸`
		cartDiv.appendChild(el)
	})
	totalDiv.innerHTML = `<h3>Итого: ${total}₸</h3>`
}
