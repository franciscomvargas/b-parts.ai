var element = $('.floating-chat');

setTimeout(function() {
    element.addClass('enter');
}, 1000);

element.click(openElement);

function openElement() {
    var messages = element.find('.messages');
    var textInput = element.find('.text-box');
    element.find('>i').hide();
    element.addClass('expand');
    element.find('.chat').addClass('enter');
    var strLength = textInput.val().length * 2;
    textInput.keydown(onMetaAndEnter).prop("disabled", false).focus();
    element.off('click', openElement);
    element.find('.header button').click(closeElement);
    element.find('#sendMessage').click(sendNewMessage);
    messages.scrollTop(messages.prop("scrollHeight"));
}

function closeElement() {
    element.find('.chat').removeClass('enter').hide();
    element.find('>i').show();
    element.removeClass('expand');
    element.find('.header button').off('click', closeElement);
    element.find('#sendMessage').off('click', sendNewMessage);
    element.find('.text-box').off('keydown', onMetaAndEnter).prop("disabled", true).blur();
    setTimeout(function() {
        element.find('.chat').removeClass('enter').show()
        element.click(openElement);
    }, 500);
}


// 👇 WEBSOCKET UTILS BELLOW 👇
const socket = new WebSocket("ws://localhost:9000");
var msgI = 0
// Event listener for connection open
socket.addEventListener('open', (event) => {
    console.log('WebSocket connection opened');
});
// Event listener for connection close
socket.addEventListener('close', (event) => {
    console.log('WebSocket connection closed'); 
});
// Event listener for connection errors
socket.addEventListener('error', (event) => {
    console.error('WebSocket error:', event.error);
});

// Event listener for receiving messages
var curr_msg_id = 0
socket.addEventListener('message', (event) => {
    const message = event.data;
    displayMessage(message);
});
function displayMessage(message) {
    console.log(message)
    document.getElementById('msg'+msgI).innerHTML=message
}
// 👆 WEBSOCKET UTILS ABOVE  👆


function createUUID() {
    // http://www.ietf.org/rfc/rfc4122.txt
    var s = [];
    var hexDigits = "0123456789abcdef";
    for (var i = 0; i < 36; i++) {
        s[i] = hexDigits.substr(Math.floor(Math.random() * 0x10), 1);
    }
    s[14] = "4"; // bits 12-15 of the time_hi_and_version field to 0010
    s[19] = hexDigits.substr((s[19] & 0x3) | 0x8, 1); // bits 6-7 of the clock_seq_hi_and_reserved to 01
    s[8] = s[13] = s[18] = s[23] = "-";

    var uuid = s.join("");
    return uuid;
}
const CLIENT_ID = createUUID()

function sendNewMessage() {
    var userInput = $('.text-box');
    var newMessage = userInput.html().replace(/\<div\>|\<br.*?\>/ig, '\n').replace(/\<\/div\>/g, '').trim().replace(/\n/g, '<br>');

    if (!newMessage) return;

    var messagesContainer = $('.messages');

    messagesContainer.append([
        '<li class="self">',
        newMessage,
        '</li>'
    ].join(''));

    // clean out old message
    userInput.html('');
    // focus on input
    userInput.focus();

    messagesContainer.finish().animate({
        scrollTop: messagesContainer.prop("scrollHeight")
    }, 250);


    // 👇 WEBSOCKET LOGIC BELLOW 👇
    socket.send(CLIENT_ID+"|"+newMessage);
    msgI++;
    // Placeholder for WebSocket result UI update
    messagesContainer.append([
        '<li class="other" id=msg'+msgI+'>',
        'Awaiting response...', // Placeholder until WebSocket response is received
        '</li>'
    ].join(''));
    // 👆 WEBSOCKET LOGIC ABOVE  👆


    messagesContainer.finish().animate({
        scrollTop: messagesContainer.prop("scrollHeight")
    }, 250);
}

function onMetaAndEnter(event) {
    if ((event.metaKey || event.ctrlKey) && event.keyCode == 13) {
        sendNewMessage();
    }
}
