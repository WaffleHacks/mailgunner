FROM python:3.8-slim as base

# Python environment variables
ENV DJANGO_SETTINGS_MODULE mailgunner.settings
ENV PYTHONUNBUFFERED 1
ENV PYTHONFAULTHANDLER 1

WORKDIR /mailgunner

# Install global dependencies
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends libmagic1 libpq-dev


# Export dependences from poetry
FROM base as export-dependencies

# Install poetry
RUN pip install --no-cache-dir poetry

# Install dependencies
COPY poetry.lock pyproject.toml ./

# Export to requirements format
RUN poetry export -f requirements.txt -o requirements.txt


# Base image for building
FROM base as builder

# Install build dependencies
RUN apt-get install -y --no-install-recommends build-essential

# Install dependencies
COPY --from=export-dependencies /mailgunner/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt --prefix=/dependencies

# Copy project files
COPY account ./account/
COPY conversations ./conversations/
COPY mailgunner ./mailgunner/
COPY schedule ./schedule/
COPY static ./static/
COPY templates ./templates/
COPY utils ./utils/
COPY manage.py ./


# Compile static assets
FROM builder as static-assets

# Move dependencies to global level
RUN cp -r /dependencies/* /usr/local

# Compile assets
RUN SECRET_KEY=assets python manage.py collectstatic --no-input


# Assemble all the previous images
FROM base as assembled

# Copy project files
COPY --from=builder /mailgunner /mailgunner

# Remove unused files
RUN rm -rf requirements.txt static

# Copy built files
COPY --from=builder /dependencies /usr/local
COPY --from=static-assets /mailgunner/staticfiles ./staticfiles


###
# Django image
###
FROM assembled as django
EXPOSE 8000
COPY --chmod=775 docker-entrypoint.sh ./entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]


###
# Celery image
###
FROM assembled as celery
ENTRYPOINT ["celery", "-A", "mailgunner", "worker", "-l", "INFO"]
