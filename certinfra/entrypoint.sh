#!/bin/bash

cd /app
mkdir -p /certdata/.CA/private /certdata/.CA/certs
ansible-playbook playbook.yml
cat > /vhostdata/keycloak.localdomain <<EOF
location ~ ^/auth/.*/auth$ {
  add_header 'Access-Control-Allow-Origin' '*' always;
  add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS' always;
  add_header 'Access-Control-Allow-Headers' 'Authorization,DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type' always;
  add_header 'Access-Control-Expose-Headers' 'Access-Control-Allow-Methods' always;
  if (\$request_method = OPTIONS) {
    return 204;
  }
  proxy_pass http://keycloak.localdomain;
}
EOF
socat /dev/null,ignoreeof tcp-listen:8080,fork,reuseaddr
