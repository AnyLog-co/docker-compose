# require ubuntu 22.04
cd $HOME

wget https://images.nextensio.net/field-trials/linux-ubuntu/nextender-agent-authz-code-spa-pkce-cli-1.1.44.2204.tgz

tar -xzvf nextender-agent-authz-code-spa-pkce-cli-1.1.44.2204.tgz

cp -r nextender-agent /tmp/

screen -Sd nextensio -m bash -c "NXT_USERNAME=ori@anylog.co NXT_PWD=\!TestOps10\! /tmp/nextender-agent/utils/deploy-extender-agnt --log-path /tmp/nextsio.log --allow-requests-from 137.184.181.13"