# SKAI ERP

SKAI Technologies ERP System

## Development
- Use [frappe-docker](https://github.com/frappe/frappe_docker/blob/main/docs/development.md) for custom app development
- Push the custom app to github once it is tested
- Add app details to `docker/apps.json` in this repo

## Testing
```
APPS_JSON_BASE64=$(openssl base64 -in docker/apps.json) # Mac
# APPS_JSON_BASE64=$(base64 -w 0 docker/apps.json) # Linux

docker build \
  --build-arg=FRAPPE_PATH=https://github.com/frappe/frappe \
  --build-arg=FRAPPE_BRANCH=version-15 \
  --build-arg=PYTHON_VERSION=3.11.6 \
  --build-arg=NODE_VERSION=18.18.2 \
  --build-arg=APPS_JSON_BASE64=$APPS_JSON_BASE64 \
  --tag=ghcr.io/skaiworld/skai-erp:v15 docker

docker compose up
```
Check http://localhost

## Production

SKAI ERP can be deployed to production server via docker. Choose an Ubuntu VM or docker hosting that supports `docker-compose.yml`

- Push `main` branch to Github to build and push docker image via github actions.
- ssh into Ubuntu machine `ssh ubuntu@ip`
- Install docker - Run:
  ```
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
  sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu focal stable" -y
  sudo apt install docker-ce -y
  sudo usermod -aG docker ${USER}
  sudo su - ${USER}
  ```
- Run `docker compose up -d`
- Open port 80 to users
