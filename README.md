# User tasks

## Usage

To start the server, run the following command:

```bash
# manage.py migrate command is called automatically on container startup
docker compose up --build
```

To create a superuser, run:

```bash
docker exec -it user-task /bin/bash

# this run inside the container
python manage.py createsuperuser
```

