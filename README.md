# Overview
This is a simple python server that I (Thomas O'Keeffe) created because I thought many other servers (Apache, Nginx, etc) were too complex and resource intensive for simple applications.
Great for use in a testing environment, or as I use it, for remote managing networks of sensors.

As a result, this server is a (relatively) small and easily extensible **boilerplate** that can be extended through python and any language that can interface with python.
Note: This is not a server architecture. It is boilerplate code for you to modify to fit your needs.

Launching the server "as is" is simple. Just open a terminal in the root package directory and run `sudo ./startup.py`. You can then navigate to `https://localhost` (you may need to add a security exception) and watch the random numbers appear.

The username is `guest` and the password is `password`. This is configurable in the `passwd` file.
# Basic Functionality

### Things included
* Login system using cookies
* Websocket integration
* Easy python integration (obviously extends to languages that interface with python)
* Threading. The server is fully multi-thread capable
* Http redirection. When a user attempts to connect using http, they are forwarded to https
* Basic template pages with a tiny bit of injected code


### Things not included
* A fully fledged html injector. This will not change. You provide your web files and html parser/injector (if needed), because everyone's case is different. There is, of course, a system in place to run the parser/injector should you choose to have one.
* Templates beyond the test pages
* Real SSL certificates. The certs in the `.ssl` directory are just for `localhost` and they are self-signed (which is why you'll need to add a security exception) so you'll [need your own](https://zerossl.com/).

# Quickstart
* All website related files are in web/
* You should rewrite HtmlInjector to fit your needs as well as config.json (changing all HtmlInjector methods to `pass` and setting config.json to `{}` is fine)
* The server projects to `localhost` by default, this is controlled by `startup.py`'s global `DOMAIN` (all files use `startup.DOMAIN` so no need to hardcode)
* Backend.py is just an example (obviously), as is `TransferManager`. They are just there to show one possible way to get data from the backend to the front.
* `script.js` and `WebSocketManager.py` are intimately related so be careful what you send through. All messages sent over the websocket **must** be strings!

# FAQ
Q. Why is the password loading and auth system written in python?
<br>
A. I'm working on rewriting it in a C like language (Rust) once I finish my Rust course
<br>
<br>
Q. Why doesn't it work to test it work to test it on Firefox?
<br>
A. I don't know, I use Chrome for testing (regrettably) because I couldn't get it to work

# Contact
Feel free to hit me up at nitrogen1818 (at) gmail (dot) com with any questions or concerns.
