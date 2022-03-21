# Workshop - GraphAware Hume's Orchestra

This repository contains a trial version of Hume 2.11 for workshop purposes. Participants will receive credentials to access the GraphAware Docker Registry.

## Requirements

- A laptop or a server with 5-6GB of memory.
- Docker and Docker Compose installed

## Installation

The following procedure will install the necessary containers for running Hume:

- Neo4j 4.4.4
- Hume

Plus other necessary services, such as:
- Minio
- RabbitMQ
- PostgreSQL

### Login to the GraphAware Docker registry

```bash
docker login docker.graphaware.com
```

and provide the credentials that have been given to you during the registration.

### Pull the containers

```
docker-compose pull
```

### Start Hume

```
docker-compose up -d
```

it can take some minutes to start depending on your machine.

### Inspect logs

If something is not working as expected, inspect the logs :

```
docker-compose logs -f
```

### Test the installation and create the admin user
Head to http://localhost:8081 (opens new window), the interface will prompt you to create a new admin user for Hume.
Specify username and password. Please save them.

### License installation
After the admin creation you will be redirect to the login page, after the login you'll be redirect to the License page since the tool comes without license. 
Please upload the file provided to you before the workshop. 


### Recommended memory settings

#### Linux hosts

On Linux hosts, by default, a Docker container has no resource constraints and can use as much of a given resource as the kernel scheduler allows.

#### MacOS and MS Windows hosts

On Windows and Mac OS, Docker Engine runs on top of a lightweight virtual machine (VM), which can be handled via Docker Desktop.
Thus, in these environments, only a part of hosts' memory is reserved to this VM; this portion of memory represents the upper limit of the memory that Hume can use.

By default, Docker Desktop is set to use 2 GB runtime memory, allocated from the total available memory on your Mac/Windows machine.

When running Hume with these default RAM settings, if the kernel detects that there is not enough memory to perform important system functions, it throws an Out Of Memory Exception (OOME), and starts killing processes to free up memory.
For instance, in case of intensive data ingestion, Neo4j can easily run out of memory, and then its process can be killed by OOM killer.

In order to avoid this kind of events, we strongly recommend increasing the amount of RAM via Docker Desktop.
To do so, head to `Preferences -> Resources -> Advanced` and increase `Memory` at least to 6 GB.

