    const socket = new WebSocket("wss://fishy.wiki/ws");
        var msgI = 0
            // Event listener for connection open
    socket.addEventListener('open', (event) => {
        console.log('WebSocket connection opened');
    });
    // Event listener for receiving messages
    socket.addEventListener('message', (event) => {
        const message = event.data;
        displayMessage(message);
    });
    function displayMessage(message) {
        document.getElementById('msg'+msgI).innerHTML=message
    }
    // Event listener for connection close
    socket.addEventListener('close', (event) => {
        console.log('WebSocket connection closed'); 
    });
    // Event listener for connection errors
    socket.addEventListener('error', (event) => {
        console.error('WebSocket error:', event.error);
    });

    $('#send-button').click(() => {
        const messageInput = $('#messageIn').val();
        if (messageInput.trim() !== '') {
            socket.send("{/literal}{$this->context->customer->id}{literal}|"+messageInput);
            $('#messageIn').val('');
            msgI++
            const messageElement1 = <div  class="message anim" style="--delay: .1s">
            <div class="msg-wrapper-you">
         <div class="msg__you offline"> You</div>
         <div class="msg__content video-p-sub" >${messageInput}</div>
        </div>
       </div>;
            $('.message-container').append(messageElement1);
            msgI++
            const messageElement2 = <div  class="message anim" style="--delay: .2s">
        <div class="msg-wrapper">
         <div class="msg__name video-p-name"> Fishy Assistant</div>
         <div class="msg__content video-p-sub" id='msg${msgI}'>...</div>
        </div>
       </div>;
            $('.message-container').append(messageElement2);
        }
    });