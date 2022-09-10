let updateBtns = document.getElementsByClassName('update-cart')

for (i = 0; i < updateBtns.length; i++) {
	updateBtns[i].addEventListener('click', function(){ //for each button add eventlistener that reacts to each click
		let productId = this.dataset.product
		let action = this.dataset.action 
		console.log('productId:', productId, 'Action:', action)

        console.log('USER:', user)
		if (user == 'AnonymousUser'){
			addCookieItem(productId, action)	
		}else{ 
			updateUserOrder(productId, action)
			}
    })
}

function addCookieItem(productId, action){

	// cart - a JavaScript object, received in main.html in a function getCookie, by parsing cookies

	if (action=='add') {if (
		cart[productId]== undefined ){
			cart[productId]={'quantity':1};
			} else{
				cart[productId]['quantity'] +=1
			}
	}

	if (action=='remove') {
		cart[productId]['quantity'] -=1

		if(cart[productId]['quantity']<=0){ //remove item if quantity <=0
			delete cart[productId]
		}
	}

	document.cookie ='cart=' + JSON.stringify(cart) + ";domain=;path=/" //set our cookies to the domain
	console.log('CART:', cart)

	location.reload() //reload the page

}

function updateUserOrder(productId, action){
	console.log('User is authenticated, sending data...')

		let url = '/update_item/' //send POST data to this view - updateItem

		fetch(url, {
			method:'POST',
			headers:{
				'Content-Type':'application/json',
                'X-CSRFToken':csrftoken,
			}, 
			body:JSON.stringify({'productId':productId, 'action':action}) //data sent to the backend
		})
		.then((response) => {
		   return response.json();
		})
		.then((data) => {
		    location.reload()
		});
}
