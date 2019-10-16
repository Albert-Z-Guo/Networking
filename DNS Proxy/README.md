# Networking

## Project Description
Part 1: <br />
A DNS proxy which listens on port `53` for DNS queries, forwards those queries to a single upstream DNS resolver, waits for an answer from the upstream resolver, and forwards the answer back to the client.

Part 2: <br />
A DNS over HTTPS wrapper which has mainly two functionalities: it will parse the DNS over UDP packet from client and convert it into a DNS over HTTPS request, and forward the request to an actual DNS resolver that supports DoH.

Part 3: <br />
Optimizing Part 2 by setting up only one session on the first time making a request, and keeping the same session alive for the rest of the requests. A `time.txt` file is generated to measure the response times.

### Team Members:
- Zunran Guo (ZGU682) [@Albert-Z-Guo](https://github.com/Albert-Z-Guo)
