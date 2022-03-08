# Deploy Grafana as a docker image
docker run -d -p 3000:3000 \
  --name=grafana \
  -v grafana-data:/var/lib/grafana \
  -v grafana-log:/var/log/grafana \
  -v grafana-config:/etc/grafana \
  -e "GF_INSTALL_PLUGINS=simpod-json-datasource,grafana-worldmap-panel" \
  --rm grafana/grafana:7.5.7
