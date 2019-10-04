# Networking

## Project Description
Part 1: <br />
A DNS proxy which listens on port `53` for DNS queries, forwards those queries to a single upstream DNS resolver, waits for an answer from the upstream resolver, and forwards the answer back to the client.

Part 2: <br />
A DNS over HTTPS wrapper which has mainly two functionalities: it will parse the DNS over UDP packet from client and convert it into a DNS over HTTPS request, and forward the request to an actual DNS resolver that supports DoH.

### Team Members:
- Manshan Lin [@linmanshan](https://github.com/linmanshan)
- Zunran Guo [@Albert-Z-Guo](https://github.com/Albert-Z-Guo)
