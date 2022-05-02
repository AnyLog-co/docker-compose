# Deploy Grafana as a docker image
docker run -d -p 3000:3000 --name=grafana --rm \
  -e GRAFANA_ADMIN_USER=admin \
  -e GRAFANA_ADMIN_PASSWORD=passwd \
  -e GF_AUTH_DISABLE_LOGIN_FORM=false \
  -e GF_AUTH_ANONYMOUS_ENABLED=true \
  -e GF_SECURITY_ALLOW_EMBEDDING=true \
  -e "GF_INSTALL_PLUGINS=simpod-json-datasource,grafana-worldmap-panel" \
  -v grafana-data:/var/lib/grafana \
  -v grafana-log:/var/log/grafana \
  -v grafana-config:/etc/grafana \
  grafana/grafana:8.2.6
