# SKAI ERP

SKAI Technologies ERP System

## Development
- Use [frappe-docker](https://github.com/frappe/frappe_docker/blob/main/docs/development.md) for custom app development
- Push the custom app to github once it is tested
- Add app details to `docker/apps.json` in this repo

## Testing
- Copy `example.env` to `.env`
- (May need `docker builder prune -a` to clear build cache)
```
APPS_JSON_BASE64=$(openssl base64 -in docker/apps.json) # Mac
# APPS_JSON_BASE64=$(base64 -w 0 docker/apps.json) # Linux

docker build \
  --build-arg=FRAPPE_PATH=https://github.com/frappe/frappe \
  --build-arg=FRAPPE_BRANCH=version-15 \
  --build-arg=PYTHON_VERSION=3.11.6 \
  --build-arg=NODE_VERSION=18.18.2 \
  --build-arg=APPS_JSON_BASE64=$APPS_JSON_BASE64 \
  --tag=ghcr.io/skaiworld/skai-erp:develop docker

docker compose -f docker.base.yml -f docker.dev.yml up -d
```
Check http://localhost

## Production

SKAI ERP can be deployed to production server via docker. Choose an Ubuntu VM or docker hosting that supports `docker-compose.yml`

- Push `develop` branch or `v*` tag to Github to build and push docker image via github actions.
- Copy files `scp docker.base.yml docker.prod.yml configurator.py .env ubuntu@ip:~/`
- ssh into Ubuntu machine `ssh ubuntu@ip`
- Edit `.env` file
- Install docker - Run:
  ```
  sudo apt-get update
  sudo install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
  sudo chmod a+r /etc/apt/keyrings/docker.gpg
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
  sudo apt-get update
  sudo apt install docker-ce -y
  sudo usermod -aG docker ${USER}
  sudo su - ${USER}

  # Temporary: Disable firewall
  # https://www.cyberciti.biz/tips/linux-iptables-how-to-flush-all-rules.html
  ```
- Run `docker compose -f docker.base.yml -f docker.prod.yml up -d`
- (Remove unused images `docker image prune -a`)
- Open port 80 to users

## Others

### Helpful commands for testing
- `docker exec -u 0 -it skai-erp-frontend bash` Exec bash in container as root
- `BENCH_SECRET=secret ADDRESS=localhost ADMIN_PASSWORD='admin' python3 ./docker/bench_server.py` ro test bench server
