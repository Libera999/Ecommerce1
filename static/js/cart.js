let updateBtns = document.getElementsByClassName('update-cart')

for (i = 0; i < updateBtns.length; i++) {
	updateBtns[i].addEventListener('click', function(){ //for each button add eventlistener that reacts to each click
		let productId = this.dataset.product
		let action = this.dataset.action 
		console.log('productId:', productId, 'Action:', action)

        console.log('USER:', user)
		if (user == 'AnonymousUser'){
			console.log('User is not authenticated')
			
		}else{ updateUserOrder(productId, action)
			
		}
    })
}

function updateUserOrder(productId, action){
	console.log('User is authenticated, sending data...')

		let url = '/update_item/' //send POST data here to this view

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
