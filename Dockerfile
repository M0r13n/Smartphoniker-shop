ARG INSTALL_PYTHON_VERSION=${INSTALL_PYTHON_VERSION:-3.8}
FROM python:${INSTALL_PYTHON_VERSION}-slim-buster AS base
LABEL maintainer="Leon Morten Richter <leon.morten@gmail.com>"

# Install minimal dependencies which are not included in the python image
RUN apt-get update
RUN apt-get install -y \
    curl \
    gcc \
    make


WORKDIR /app

# copy everything except files listed in the .dockerignore
COPY . .

# add a new user for running the app and transfer ownership of the application
RUN useradd -m pricy
RUN chown -R pricy:pricy /app
USER pricy

# add /home/pricy/.local/bin' to PATH
ENV PATH="/home/pricy/.local/bin:${PATH}"


# ================================= DEVELOPMENT ================================
FROM base AS development

RUN pip install --user -r ./requirements/requirements_dev.txt

EXPOSE 5000

CMD [ "python", "manage.py", "run", "-h", "0.0.0.0" ]

# ================================= TEST ================================
FROM base AS test

RUN pip install --user -r ./requirements/requirements_dev.txt

CMD [ "make", "test" ]

# ================================= PRODUCTION =================================
FROM base AS production

RUN pip install --user -r ./requirements/requirements_prod.txt

COPY supervisord.conf /etc/supervisor/supervisord.conf
COPY supervisord_programs /etc/supervisor/conf.d

EXPOSE 5000

ENTRYPOINT ["/bin/bash", "shell_scripts/supervisord_entrypoint.sh"]

CMD ["-c", "/etc/supervisor/supervisord.conf"]