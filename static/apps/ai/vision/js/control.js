var ws;

const host_textfield = document.getElementById('host_textfield');
const host_submitbutton = document.getElementById('host_submitbutton');
host_submitbutton.addEventListener('click', function() {
    ws = new WebSocket(host_textfield.value);
    ws.onopen = function() {
        console.log('websocket connection established.');
    };
    ws.onmessage = function(event) {
        console.log(event.data);
    };
});

const asgi_textfield = document.getElementById('asgi_textfield');
const asgi_submitbutton = document.getElementById('asgi_submitbutton');
asgi_submitbutton.addEventListener('click', function() {
    ws.send(asgi_textfield.value);
});
