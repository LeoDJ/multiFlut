# MultiFlut
A distributed pixelflut client to really pwn those large bandwidth pixelflut installations at chaos events.

## Current Status
WIP, currently looking into improving the performance of the client as it now needs to convert pixels to pixelflut strings in real time instead of converting it beforehand like [gifFlut](https://github.com/LeoDJ/gifFlut) did.

## Client / Server protocol

| Sender | Step               | Protocol | Port        | Payload         | Example Packet                                            |
| ------ | ------------------ | -------- | ----------- | --------------- | --------------------------------------------------------- |
| Client | Server discovery   | UDP BC   | $serverPort | type            | `{"type": "discovery"}`                                   |
| Server | Discovery Response | TCP      | $clientPort | type, server_ip | `{"type": "discovery_response", "server_ip": "10.1.2.3"}` |
| Client | Heartbeat          | TCP      | $serverPort | type            | `{"type": "heartbeat"}`                                   |
| Client | Disconnect         | TCP      | $serverPort | type            | `{"type": "disconnect"}`                                  |

Currently debating how to distribute picture data to clients, WIP.