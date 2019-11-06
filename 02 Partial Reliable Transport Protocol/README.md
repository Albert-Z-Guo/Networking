# Selective Repeat and Go-Back-N Protocols

## Project Description
This project implements Selective Repeat and Go-Back-N protocols. The emulated UDP connection is expected to drop and corrupt packets randomly.

### Message format
The sender will be called by user to send arbitrary payloads. Each payload will form a MSG packet and managed by the sender for delivery.
 - The first two bytes of each MSG packet should be the sequence number that identifies the packet.
 - The last two bytes of each MSG packet should be the checksum that makes sure the packet is not corrupted.

The receiver will acknowledge the successful delivery of packets by sending ACK packets. 
 - The first two bytes of each ACK packet should be the starting position of current receiver window. 
 - The last two bytes of each ACK packet should be the checksum that makes sure the packet is not corrupted. If a packet is corrupted, the receiver should drop that packet. 

The payload of each ACK packet contains `1` denoting successful deliveries or `0` otherwise. From the ACK packet, the sender should be able to perceive the receiver's window status, and slide the window forwards as necessary. 

### How to run
#### To start the sender: <br/>
```python
python3 start_sender.py IP PORT ALLOWED_LOSS WINDOW_SIZE LOSS_RATE CORRUPT_RATE
```

Parameters: <br/>
`IP`: The receiver’s IP address <br/>
`PORT`: The receiver’s listening port <br/>
`ALLOWED_LOSS`: The allowed loss rate for the protocol <br/>
`WINDOW_SIZE`: The window size for the sliding window <br/>
`LOSS_RATE`: The rate at which packets will be dropped when sending and receiving <br/>
`CORRUPT_RATE`: The rate at which packets will be corrupted when sending and receiving <br/>

#### To start the receiver: <br/>
```python
python3 start_receiver.py PORT ALLOWED_LOSS WINDOW_SIZE LOSS_RATE CORRUPT_RATE
```

Parameters: <br/>
`PORT`: The receiver’s listening port <br/>
`ALLOWED_LOSS`: The allowed loss rate for the protocol <br/>
`WINDOW_SIZE`: The window size for the sliding window <br/>
`LOSS_RATE`: The rate at which packets will be dropped when sending and receiving <br/>
`CORRUPT_RATE`: The rate at which packets will be corrupted when sending and receiving <br/>
 
#### To run unit tests: <br/>
```python
python3 test.py
```

### Team Members:
- Zunran Guo (ZGU682) [@Albert-Z-Guo](https://github.com/Albert-Z-Guo)
- Manshan Lin (MLW3472) [@linmanshan](https://github.com/linmanshan)