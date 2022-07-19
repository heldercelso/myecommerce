var updateBtns = document.getElementsByClassName('update-cart')
// console.log(updateBtns);

for (i = 0; i < updateBtns.length; i++) {
	updateBtns[i].addEventListener('click', function(){
		var Slug = this.dataset.slug;
		var Pk = this.dataset.pk;
		var action = this.dataset.action;
		// console.log('Slug:', Slug, 'Pk:', Pk, 'Action:', action);

		if (user == 'AnonymousUser'){
			addCookieItem(Slug, Pk, action);
		}
		// }else{
		// 	updateUserOrder(Slug, Pk, action);
		// }
	})
}

function addCookieItem(Slug, Pk, action){
	console.log('User is not authenticated');
	key = Slug+'/'+Pk;
	if (action == 'add'){
		if (cart[key] == undefined){
		cart[key] = {'quantity': 1};

		}else{
			cart[key]['quantity'] += 1;
		}
	}

	if (action == 'remove'){
		cart[key]['quantity'] -= 1;

		if (cart[key]['quantity'] <= 0){
			console.log('Item should be deleted');
			delete cart[key];
		}
	}

	if (action == 'delete'){
		delete cart[key];
	}
	console.log('CART:', cart);
	document.cookie ='cart=' + JSON.stringify(cart) + ";domain=;path=/;max-age=604800" //1 week
	
	location.reload()
}

// function updateUserOrder(Slug, Pk, action){
// 	console.log('User is authenticated, sending data...')

// 		var url = '/update_item/'

// 		fetch(url, {
// 			method:'POST',
// 			headers:{
// 				'Content-Type':'application/json',
// 				'X-CSRFToken':csrftoken,
// 			}, 
// 			body:JSON.stringify({'productId':productId, 'action':action})
// 		})
// 		.then((response) => {
// 		   return response.json();
// 		})
// 		.then((data) => {
// 		    location.reload()
// 		});
// }