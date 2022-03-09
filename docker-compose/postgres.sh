docker run -d -p 5432:5432 --name=database --rm \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=passwd \
  --health-cmd "pg_isready"
  --health-interval=10s \
  --health-timeout 5s \
  --health-retries 3 \
  -v pgdata:/var/lib/postgresql/data \
  postgres:14.0-alpine
