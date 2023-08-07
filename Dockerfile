# Basic python3 image as base
FROM harbor2.vantage6.ai/infrastructure/algorithm-base:3.4.2


# This is a placeholder that should be overloaded by invoking
# docker build with '--build-arg PKG_NAME=...'
ARG PKG_NAME="v6-healthai-dashboard-py"

RUN apt-get update
RUN apt-get install -y apt-utils gcc libpq-dev wget iputils-ping

# Install federated algorithm
COPY . /app
RUN pip install /app

# Tell docker to execute `docker_wrapper()` when the image is run.
ENV PKG_NAME=${PKG_NAME}
CMD python -c "from vantage6.tools.docker_wrapper import docker_wrapper; docker_wrapper('${PKG_NAME}')"
