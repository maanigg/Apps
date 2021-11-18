document.addEventListener('DOMContentLoaded', () => {
    
    // Create the websocket (real-time connection between server and client)
    var socket = io.connect('http://' + document.domain + ':' + location.port);
    // Grab the user's local storage
    var my_storage = window.localStorage;
    // Execute when the user connects to the websocket
    socket.on('connect', () => {
        // If the user was in a room before they left send them back to that room
        if (my_storage.getItem('channel')) {
        
            socket.emit("join_channel", my_storage.getItem('channel'));
        }
        else {
            document.querySelector("#chat").style.display = "none";
        }
        
    });
    document.querySelector("#create_channel").onsubmit = () => {
        // Emit the channel creation event using the input from the user
        const channel = document.querySelector("#channel").value;
        socket.emit("channel_creation", channel);
        // Prevent form submission
        return false;
    };

});