if ("WebSocket" in window) {
	// Let us open a web socket
	const socket = new WebSocket("wss://localhost:8000");

	socket.addEventListener('message', function (event) {
	    	var message = event.data;
	    	$("div").text(message);
	});
} else {
	window.alert("Websockets are not supported. This webpage WILL NOT WORK!");
}
