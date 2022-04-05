## Auto Update CloudFlare DNS Records With Python
This program will automatically update your CloudFlare DNS records with the IP address of your local machine every time it chnages.

## Requirements
- Python 3.6+
- pip
- requests
- pyyaml
- cloudflare


## Installation
1. Clone the repository `git clone`
2. Install the requirements `pip3 install -r requirements.txt`
3. Create a config file `cp config.yml.example config.yml`
4. Fill in the config file with your CloudFlare API key and domain name
5. Done, Set the program as a service or cron job


