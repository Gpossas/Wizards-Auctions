function changeWatchlistState(url){
    fetch(url, {
        method: 'POST',
        headers: {'X-CSRFToken': csrftoken},
        mode: 'same-origin', // Do not send CSRF token to another domain.  
        body: JSON.stringify({ watchlist: watchlist.value }),
    })
    .then(async response => {
        if (response.ok){
            return response.json();
        } else{
            const error = await response.json().then(message => message['error']);
            const flash = addFlashMessage('alert-danger', error);
            removeFlashMessage(flash);
            throw new Error(`Error: ${error}, status: ${response.status}`);
        }
    })
    .then(data => {
        if (data['action'] == 'add'){
            toggleButtonWatchlist('in_watchlist', 'btn-outline-primary', 'btn-primary', 'Remove from watchlist');
            const flash = addFlashMessage('alert-success', 'Added to watchlist');
            removeFlashMessage(flash);
        }
        else{
            toggleButtonWatchlist('', 'btn-primary', 'btn-outline-primary', 'Add to watchlist');
            const flash = addFlashMessage('alert-danger', 'Deleted from watchlist');
            removeFlashMessage(flash);
        }
    })
    .catch(error =>{
        console.log(error.message);
    });
}

function changeBidState(url){
    fetch(url, {
        method: 'POST',
        headers: {'X-CSRFToken': csrftoken},
        mode: 'same-origin', // Do not send CSRF token to another domain.  
        body: JSON.stringify({ bid: bid.value }),
    })
    .then(async response => {
        if (response.ok){
            return response.json();
        } else{
            const error = await response.json().then(message => message['error']);
            const flash = addFlashMessage('alert-danger', error);
            removeFlashMessage(flash);
            bid.value = '';
            throw new Error(`Error: ${error}, status: ${response.status}`);
        }
    })
    .then(data => {
        const flash = addFlashMessage('alert-success', data['message']);
        removeFlashMessage(flash);
        bid.value = '';
        bidPrice.innerText = `$ ${data['bid']}`;
    })
    .catch(error =>{
        console.log(error.message);
    });
}

function addFlashMessage(class_name, text){
    const flash = document.createElement('p');
    flash.className = `alert ${class_name}`;
    flash.innerText = text;
    flashMessage.appendChild(flash);
    return flash
}

function removeFlashMessage(flashMessage){
    setTimeout(() => flashMessage.remove(), 3000);
}

function toggleButtonWatchlist(value, remove, add, text){
    watchlist.value = value;
    watchlist.classList.remove(remove);
    watchlist.classList.add(add);
    watchlist.innerHTML = text;
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// https://docs.djangoproject.com/en/4.2/howto/csrf/
const csrftoken = getCookie('csrftoken');
const flashMessage = document.querySelector('.flash_message');
const watchlist = document.querySelector('#watchlist');
const bidButton = document.querySelector('#bid_button');
const bid = document.querySelector('#bid');
const bidPrice = document.querySelector('#bid_price');
watchlist.addEventListener('click', () => changeWatchlistState(watchlist.dataset.action));
bidButton.addEventListener('click', () => changeBidState(bidButton.dataset.action));