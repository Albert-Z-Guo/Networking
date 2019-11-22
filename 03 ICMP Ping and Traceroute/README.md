# ICMP Ping and Traceroute

## Project Description
Part 1: <br />
`ping.py` measures the round-trip time (RTT), records packet loss, and prints a statistical summary of the echo reply packets received (minimum, maximum, mean, and standard deviation of RTTs).

Part 2: <br />
`traceroute.py` traces the route from a host to any other host in the world. It sends ICMP echo (ICMP type `8`) messages to the same destination with increasing value of the time-to-live (TTL) field. The routers along the traceroute path return ICMP Time Exceeded (ICMP type `11` ) messages when the TTL field become zero. The final destination sends an ICMP reply (ICMP type `0` ) messages on receiving the ICMP echo request.

### Team Members:
- Zunran Guo (ZGU682) [@Albert-Z-Guo](https://github.com/Albert-Z-Guo)
- Manshan Lin (MLW3472) [@linmanshan](https://github.com/linmanshan)
