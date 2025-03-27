# SKAI ERP

SKAI Technologies ERP System

## Development
- Use [frappe-docker](https://github.com/frappe/frappe_docker/blob/main/docs/development.md) for custom app development
- Push the custom app to github once it is tested
- Add app details to `docker/apps.json` in this repo

## Testing
- Copy `example.env` to `.env` and update if needed
- (May need `docker builder prune -a` to clear build cache)
- Run `./deploy.sh -e local`
- Check http://localhost

## Production

SKAI ERP can be deployed to production server via docker. Choose an Ubuntu VM or docker hosting that supports `docker-compose.yml`

- Push `develop` branch or `v*` tag to Github to build and push docker image via github actions.
- Copy `example.env` to `.env.demo` and `.env.prod` and update

### First time setup
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
- Set timezone `sudo timedatectl set-timezone Asia/Kolkata`
- Open port 80 to users

### Deployment
- Run `./deploy.sh -e demo` or Run `./deploy.sh -e prod`
- Run `./deploy.sh -e demo -b` or `./deploy.sh -e prod -b` to run build assets
- Run `./deploy.sh -e demo -m` or `./deploy.sh -e prod -m` to run bench migrate
- (Remove unused images `docker image prune -a`)

## Deploy script
`deploy.sh` is used for automating build and deployment.

The default action of the deploy script is to run docker containers in the given environment. Optional arguments can be supplied to perform additional tasks.

### Arguments
- `--env, -e` (Required): Deployment environment. Eg: `-e prod`
- `--bench-build, -b`: Run `bench build`.
- `--bench-migrate, -m`: Run `bench migrate`
- `--image-build, -i`: Build docker image. Only local. No effect in remmote environments.
- `--help, -h`: Help menu.

## Others

### Helpful commands for testing
- `docker exec -u 0 -it skai-erp-frontend bash` Exec bash in container as root
- `BENCH_SECRET=secret ADDRESS=localhost ADMIN_PASSWORD='admin' python3 ./docker/bench_server.py` ro test bench server
