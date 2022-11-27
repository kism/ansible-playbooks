ducktoken=$(cat /opt/duckdns/ducktoken)
ipv4addr=$(curl -s ipv4.icanhazip.com)
ipv6addr=$(curl -s ipv6.icanhazip.com)
url="https://www.duckdns.org/update?domains=kism&token=$ducktoken&ip=$ipv4addr&ipv6=$ipv6addr"
curl -s -k -o /var/log/duckdns.log $url