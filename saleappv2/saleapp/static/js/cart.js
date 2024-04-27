function addToCart(id, name, price) {
    fetch('/api/cart', {
        method: 'post',
        body: JSON.stringify({
            "id": id,
            "name": name,
            "price": price
        }),
        headers: {
            "Content-Type": "application/json"
        }
    }).then(res => res.json()).then(data => {
        let eles = document.getElementsByClassName('cart-counter');
        for (let d of eles)
            d.innerText = data.total_quantity;
    })
}