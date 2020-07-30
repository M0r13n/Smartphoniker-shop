ARG INSTALL_PYTHON_VERSION=${INSTALL_PYTHON_VERSION:-3.8}
FROM python:${INSTALL_PYTHON_VERSION}-slim-buster AS base

RUN apt-get update
RUN apt-get install -y \
    curl \
    gcc \
    make


WORKDIR /app

COPY . .

RUN useradd -m pricy
RUN chown -R pricy:pricy /app
USER pricy
# add /home/pricy/.local/bin' to PATH
ENV PATH="/home/pricy/.local/bin:${PATH}"

RUN pip install --user -r requirements.txt

# ================================= DEVELOPMENT ================================
FROM base AS development

EXPOSE 5000

CMD [ "python", "manage.py", "run", "-h", "0.0.0.0" ]

# ================================= PRODUCTION =================================
FROM base AS production

#COPY supervisord.conf /etc/supervisor/supervisord.conf
#COPY supervisord_programs /etc/supervisor/conf.d
#EXPOSE 5000
#ENTRYPOINT ["/bin/bash", "shell_scripts/supervisord_entrypoint.sh"]
#CMD ["-c", "/etc/supervisor/supervisord.conf"]

CMD [ "make", "run" ]

# =================================== MANAGE ===================================
FROM base AS manage

ENTRYPOINT [ "python" , "manage.py" ]