if ("WebSocket" in window) {
	// Let us open a web socket
	const socket = new WebSocket("wss://localhost:8000");

	socket.addEventListener('message', function (event) {
		let json_message = JSON.parse(event.data);
		let selected = $(json_message["css_selector"]);

		if (json_message["overwrite"] === "true") {
            selected.text(json_message["payload"]);
		} else {
			let old_text = selected.text();
			selected.text(old_text + json_message["payload"]);
		}
	});
} else {
	window.alert("Websockets are not supported. This webpage WILL NOT WORK!");
}
