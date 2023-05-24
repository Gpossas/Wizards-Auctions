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

function addComment(url){
    fetch(url, {
        method: 'POST',
        headers: {'X-CSRFToken': csrftoken},
        mode: "same-origin",
        body: JSON.stringify({comment: comment.value})
    })
    .then(async response => {
        if (response.ok){
            return response.json();
        } else{
            const error = await response.json().then(message => message['error']);
            const message = document.createElement('p');
            message.innerText = error;
            message.style.color = 'red';
            comment.parentElement.prepend(message);
            removeFlashMessage(message, 2000);
            comment.value = '';
            throw new Error(error);
        }
    })
    .then(data => {
        const newComment = htmlToElement(
            `<li class="list-group-item">
                <div class="comment-header">
                    <strong>${data['user']}</strong>
                    <span>${data['date']}</span>
                </div>
                <p>${data['text']}</p>
            </li>`
        );
        commentSection.prepend(newComment);
        comment.value = '';
    })
    .catch(error => {
        console.log(error.message)
    });
}

function addFlashMessage(class_name, text){
    const flash = document.createElement('p');
    flash.className = `alert ${class_name}`;
    flash.innerText = text;
    flashMessage.appendChild(flash);
    return flash
}

function removeFlashMessage(flashMessage, time=3000){
    setTimeout(() => flashMessage.remove(), time);
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

function htmlToElement(html){
    const template = document.createElement('template');
    html = html.trim();
    template.innerHTML = html;
    console.log(template.content.firstChild);
    return template.content.firstChild;
}

// https://docs.djangoproject.com/en/4.2/howto/csrf/
const csrftoken = getCookie('csrftoken');
const flashMessage = document.querySelector('.flash_message');
const watchlist = document.querySelector('#watchlist');
const bidButton = document.querySelector('#bid_button');
const bid = document.querySelector('#bid');
const bidPrice = document.querySelector('#bid_price');
const commentSection = document.querySelector('#comment_section');
const commentButton = document.querySelector('#comment_button');
const comment = document.querySelector('#comment');
watchlist.addEventListener('click', () => changeWatchlistState(watchlist.dataset.action));
bidButton.addEventListener('click', () => changeBidState(bidButton.dataset.action));
commentButton.addEventListener('click', () => addComment(commentButton.dataset.action));