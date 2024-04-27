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

function updateCart(productId, obj) {
    fetch(`/api/cart/${productId}`, {
        method: 'put',
        body: JSON.stringify({
            "quantity": obj.value
        }),
        headers: {
            "Content-Type": "application/json"
        }
    }).then(res => res.json()).then(data => {
        let eles = document.getElementsByClassName('cart-counter');
        for (let d of eles)
            d.innerText = data.total_quantity;

        let amounts = document.getElementsByClassName('cart-amount');
        for (let d of amounts)
            d.innerText = data.total_amount.toLocaleString("en");
    })
}

function deleteCart(productId) {
    if (confirm("Bạn chắc chắn xóa?") === true) {
        fetch(`/api/cart/${productId}`, {
            method: 'delete'
        }).then(res => res.json()).then(data => {
            let eles = document.getElementsByClassName('cart-counter');
            for (let d of eles)
                d.innerText = data.total_quantity;

            let amounts = document.getElementsByClassName('cart-amount');
            for (let d of amounts)
                d.innerText = data.total_amount.toLocaleString("en");

            let d = document.getElementById(`product${productId}`);
            d.style.display = "none";
        })
    }
}

function pay() {
    if (confirm("Bạn chắc chắn thanh toán?") === true) {
        fetch("/api/pay", {
            method: "post"
        }).then(res => {
            if (res.status === 200)
                location.reload();
            else
                alert("Hệ thống đang có lỗi! Vui lòng quay lại sau!");
        })

    }
}
