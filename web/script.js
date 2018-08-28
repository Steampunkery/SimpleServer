if ("WebSocket" in window) {
	// Let us open a web socket
	const socket = new WebSocket("wss://localhost:8000");

	socket.addEventListener('message', function (event) {
	    	var message = event.data;
	    	var text = $("div").text();
	    	$("div").text(text + message);
	});
} else {
	window.alert("Websockets are not supported. This webpage WILL NOT WORK!");
}
