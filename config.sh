# Domain and port for WSS
DOMAIN='miramontes.dev'
WSS_PORT=14501

# HTML root for your webserver. The nginx default
# on ubuntu is /var/www/html.
HTML_ROOT='/var/www/miramontes'

# Full cert chain for your domain
FULLCHAIN="/etc/letsencrypt/live/$DOMAIN/fullchain.pem"

# Private key for your domain cert
PRIVKEY="/etc/letsencrypt/live/$DOMAIN/privkey.pem"

# Set to true if you want to disable WSS and fallback to WS
WS_UNSECURE=false
