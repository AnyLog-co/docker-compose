docker run -d \
  --name openbao \
  -p 8080:8080 \
  -p 8200:8200 \
  -v openbao-config:/config \
  -v openbao-data:/data \
--rm openbao/openbao:latest