import CloudFlare
from requests import get
import yaml
from datetime import datetime

# Import Config
config = yaml.safe_load(open("config.yml"))


# Save error to log
def save_logs(error):
    print(error)
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("logs.txt", "a") as f:
        f.write(f"{current_time} - {error}\n")

# Get zone id from hostname
def get_zone_id(hostname: str, cf):
    try:
        zone = ".".join(hostname.split(".")[-2:])
        zones = cf.zones.get(params={"name": zone})
        if len(zones) == 0:
            save_logs("Could not find CloudFlare zone {zone}, please check domain {hostname}")
            return None
        return zones[0]["id"]
    except:
        save_logs("Could not get zone id")
        raise Exception("Could not get zone id")
    
def get_current_ip():
    return get('https://api.ipify.org').content.decode('utf8')

    
def update_dns():
    # Initialize Cloudflare API client
    try:
        cf = CloudFlare.CloudFlare(
            email=config['cloudflare']['email'],
            token=config['cloudflare']['global-api-key']
        )
    except:
        save_logs("Could not initialize Cloudflare API client")
        raise Exception("Could not initialize Cloudflare API client")

    # Get all zones
    for hostname in config['cloudflare']['hostnames']:
        zone_id = get_zone_id(hostname, cf)
        if zone_id:
            try:
                ip = get_current_ip()
                a_record = cf.zones.dns_records.get(zone_id, params={"name": hostname, "type": "A"})[0]
                a_record["content"] = str(ip)
                cf.zones.dns_records.put(zone_id, a_record["id"], data=a_record)
            except Exception as e:
                save_logs(f"Could not update record for {hostname}, {e}")
                exit(2)
    print("DNS updated")

def add_nameserver():
    nameservers = {"1.0.0.1", "1.1.1.1", "8.8.8.8"}
    with open("/etc/resolv.conf", "a+") as f:
        f.seek(0)
        if "nameserver" not in f.read():
            print("Adding nameservers to /etc/resolv.conf")
            [f.write(f"\nnameserver {nameserver}") for nameserver in nameservers]
        
def main():
    try:
        current_ip = get_current_ip()
        if current_ip != config['cloudflare']['current-ip']:
            print(f"Changing from {config['cloudflare']['current-ip']} to new ip adrress{current_ip}") 
            config['cloudflare']['current-ip'] = current_ip
            with open("config.yml", "w") as f:
                yaml.dump(config, f)
            update_dns()
            add_nameserver()
    except:
        add_nameserver()
        current_ip = get_current_ip()
        if current_ip != config['cloudflare']['current-ip']:
            print(f"Changing from {config['cloudflare']['current-ip']} to new ip adrress{current_ip}") 
            config['cloudflare']['current-ip'] = current_ip
            with open("config.yml", "w") as f:
                yaml.dump(config, f)
            update_dns()
            add_nameserver()

if __name__ == '__main__':
    main()
