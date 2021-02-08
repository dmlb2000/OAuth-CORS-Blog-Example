from python:3.8

run apt-get update && \
    apt-get -y install netcat openssl ca-certificates && \
    rm -rf /var/lib/apt/lists/* && \
    rm -Rf /usr/share/doc && rm -Rf /usr/share/man && \
    apt-get clean
run curl --proto '=https' --tlsv1.2 -sSfo /tmp/install.sh https://sh.rustup.rs && /bin/bash /tmp/install.sh -y && rm /tmp/install.sh
run python -m pip install --upgrade pip setuptools wheel
copy requirements.txt /app/requirements.txt
run . $HOME/.cargo/env && pip install -r /app/requirements.txt
run ansible-galaxy collection install community.general
copy app.py /app/app.py
copy index.html /app/index.html
copy playbook.yml /app/playbook.yml
copy swagger.yaml /app/swagger.yaml
copy entrypoint.sh /entrypoint.sh
run chmod +x /entrypoint.sh
expose 8080
ENTRYPOINT [ "/entrypoint.sh" ]