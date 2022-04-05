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
    
def main():
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
                ip = get('https://api.ipify.org').content.decode('utf8')
                a_record = cf.zones.dns_records.get(zone_id, params={"name": hostname, "type": "A"})[0]
                a_record["content"] = str(ip)
                cf.zones.dns_records.put(zone_id, a_record["id"], data=a_record)
            except Exception as e:
                save_logs(f"Could not update record for {hostname}, {e}")
                exit(2)
    print("Done")
if __name__ == '__main__':
    main()