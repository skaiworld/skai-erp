#!/bin/bash

while [ $# -gt 0 ]; do
  case "$1" in
	--env*|-e*)
		if [[ "$1" != *=* ]]; then shift; fi
		ENV="${1#*=}"
		;;
	--bench-build*|-b*)
		BUILD=1
		;;
	--bench-migrate*|-m*)
		MIGRATE=1
		;;
	--image-build*|-i*)
		IMAGE=1
		;;
	--stop*|-s*)
		STOP=1
		;;
	--help|-h)
	  echo "./deploy.sh -e demo -b -m -i -h";
	  echo "-e local -> Specify Environment";
	  echo "-b -> Bench build";
	  echo "-m -> Bnech migrate";
	  echo "-i -> Build Image (Only in local)";
	  echo "-h -> Show Help";
	  exit 0
	  ;;
	*)
	  >&2 printf "Error: Invalid argument\n"
	  exit 1
	  ;;
  esac
  shift
done

if [ -z "$ENV" ]; then
	echo Specify environment;
	echo Eg: ./deploy.sh -e local;
	exit 1;
fi

if [ "$STOP" = 1 ]; then
	echo Stopping $ENV;
	docker compose -f docker.base.yml -f docker.dev.yml stop;
	# Todo: Enable stopping demo and prod?
	exit 1;
fi

if [ "$ENV" = "demo" ] || [ "$ENV" = "prod" ]; then
	SERVER="skaid" && [[ "$ENV" = "prod" ]] && SERVER="skai";

	if [ "$BUILD" = 1 ] || [ "$MIGRATE" = 1 ]; then
		CMD="migrate" && [[ "$BUILD" = 1 ]] && CMD="build";
		ssh -T $SERVER <<-ENDSSH
			docker compose -f docker.base.yml -f docker.prod.yml exec frontend bash -c "
			echo Running bench $CMD as \\\$(whoami);
			bench $CMD;
			"
		ENDSSH
		exit 0;
	else
		echo Copying files from local to server
		scp docker.base.yml docker.prod.yml configurator.py .env.$ENV $SERVER:~/
		ssh -T $SERVER <<-ENDSSH
			echo Upping docker compose as \$(whoami) in server: $SERVER;
			mv .env.$ENV .env
			docker compose -f docker.base.yml -f docker.prod.yml up -d
		ENDSSH
	fi
fi

if [ "$ENV" = "local" ]; then
	if [ "$IMAGE" = 1 ]; then
		echo Running docker build
		# Run based on argument
		# docker builder prune -a
		APPS_JSON_BASE64=$(openssl base64 -in docker/apps.json);
		docker build \
		--build-arg=FRAPPE_PATH=https://github.com/frappe/frappe \
		--build-arg=FRAPPE_BRANCH=version-15 \
		--build-arg=PYTHON_VERSION=3.11.6 \
		--build-arg=NODE_VERSION=18.18.2 \
		--build-arg=APPS_JSON_BASE64="$APPS_JSON_BASE64" \
		--tag=ghcr.io/skaiworld/skai-erp:develop docker;
	fi

	if [ "$BUILD" = 1 ] || [ "$MIGRATE" = 1 ]; then
		CMD="migrate" && [[ "$BUILD" = 1 ]] && CMD="build";
		docker compose -f docker.base.yml -f docker.dev.yml exec frontend bash -c "
		echo Running bench $CMD as \$(whoami);
		bench $CMD;
		"
		exit 0;
	else
		echo Upping docker compose as $(whoami) in server: local;
		docker compose -f docker.base.yml -f docker.dev.yml up -d
		echo docker is running. Visit http://localhost
	fi
fi
