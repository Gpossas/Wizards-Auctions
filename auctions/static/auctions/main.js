function changeWatchlistState(url){
    fetch(url, {
        method: 'POST',
        headers: {'X-CSRFToken': csrftoken},
        mode: 'same-origin', // Do not send CSRF token to another domain.  
        body: JSON.stringify({ new_state: watchlist.dataset.new_state }),
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
        if (data['state'] === 'add'){
            toggleButtonStyle(watchlistButton, ['new_state', 'remove_watchlist'], 'btn-outline-primary', 'btn-primary', 'Remove from watchlist');
            const flash = addFlashMessage('alert-success', 'Added to watchlist');
            removeFlashMessage(flash);
        }
        else{
            toggleButtonStyle(watchlistButton, ['new_state', 'in_watchlist'], 'btn-primary', 'btn-outline-primary', 'Add to watchlist');
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

// function changeAuctionState(url){
//     fetch(url, {
//         method: 'POST',
//         headers: {'X-CSRFToken': csrftoken},
//         mode: 'same-origin',
//         body: JSON.stringify({change_state_to: auctionButton.dataset.change_state_to}),
//     })
//     .then(async response => {
//         if (response.ok){
//             return response.json();
//         } else{
//             const error = await response.json().then(message => message['error']);
//             const flash = addFlashMessage('alert-danger', error);
//             removeFlashMessage(flash);
//             throw new Error(`Error: ${error}, status ${response.status}`);
//         }
//     })
//     .then(data => {
//         console.log(data);
//         if (data['auction_is_active']){
//             const flash = addFlashMessage('alert-success', data['message']);
//             removeFlashMessage(flash);

//             toggleButtonStyle(auctionButton, '', 'btn-outline-secondary', 'btn-outline-danger', 'Pause auction');
            
//             const bid_input = htmlToElement(`
//                 <div class="bid-input form-group">
//                     <label for="price" class="form-label">Bid</label>
//                     <input id="bid" name="bid" required type="text" aria-label="Dollar amount" class="form-control" placeholder="$">
//                     <button id="bid_button" data-action="${data['bid_url']}" class="btn btn-primary mt-3">Place Bid</button>
//                 </div>
//             `);
//             let bidButton = document.querySelector('#bid_button');
//             auctionButton.dataset.change_state_to = "close_auction";
//             bid_div.removeChild(bid_div.children[0])
//             bid_div.appendChild(bid_input)     
//         } else{
//             const flash = addFlashMessage('alert-danger', data['message']);
//             removeFlashMessage(flash);
            
//             toggleButtonStyle(auctionButton, '', 'btn-outline-danger', 'btn-outline-secondary', 'Resume auction');

//             const alert_text = data['is_winner'] ? 'Listing no longer active, you won!' : 'Listing no longer active';
//             const bid_closed_alert = htmlToElement(`
//                 <div class="alert alert-info" role="alert">
//                 ${alert_text}
//                 </div>
//             `);
//             auctionButton.dataset.change_state_to = "open_auction";
//             bid_div.removeChild(bid_div.children[0])
//             bid_div.appendChild(bid_closed_alert)
//             bid_text.innerText.replace('Your bid is the current bid', '');
//         }
//     })
//     .catch(error => {
//         console.log(error);
//     });
// }

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

function toggleButtonStyle(element, [data_set, value], remove, add, text){
    element.dataset[data_set] = value;
    element.classList.remove(remove);
    element.classList.add(add);
    element.innerHTML = text;
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
    return template.content.firstChild;
} 

// https://docs.djangoproject.com/en/4.2/howto/csrf/
const csrftoken = getCookie('csrftoken');
const flashMessage = document.querySelector('.flash_message');
const watchlistButton = document.querySelector('#watchlist');
let bidButton = document.querySelector('#bid_button');
const bid = document.querySelector('#bid');
const bidPrice = document.querySelector('#bid_price');
const bid_div = document.querySelector('.bids');
const bid_text = document.querySelector('.bid-text');
const commentSection = document.querySelector('#comment_section');
let commentButton = document.querySelector('#comment_button');
const comment = document.querySelector('#comment');
// let auctionButton = document.querySelector('#auction_state');
watchlistButton.addEventListener('click', () => changeWatchlistState(watchlistButton.dataset.action));
bidButton.addEventListener('click', () => changeBidState(bidButton.dataset.action));
commentButton.addEventListener('click', () => addComment(commentButton.dataset.action));
// if (auctionButton) auctionButton.addEventListener('click', () => changeAuctionState(auctionButton.dataset.action));