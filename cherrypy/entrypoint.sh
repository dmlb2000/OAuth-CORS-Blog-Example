#!/bin/bash

cd /app
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
cp /certdata/pacifica_chain.io.crt /certdata/pacifica_root_ca.io.crt /usr/local/share/ca-certificates/
update-ca-certificates --fresh
ansible-playbook playbook.yml
python app.py -c config.ini