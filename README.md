# MailGunner

A web application that allows sending and receiving email through [MailGun](https://mailgun.com).

## Development

1. Install Python 3 and [Poetry](https://python-poetry.org)
2. Setup PostgreSQL and Redis

If you have Docker and Docker Compose installed, you can run `docker-compose up -d` to setup a local instance of PostgreSQL and Redis.

* The PostgreSQL instance can be connected with `postgres://postgres:postgres@127.0.0.1:5432/postgres`.
* The Redis instance can be connected with `redis://127.0.0.1:6379`.

3. Install the dependencies
```shell
$ poetry install
```
4. Get credentials for [MailGun](https://mailgun.com), [Discord OAuth2](https://discord.com/developers/applications), and [AWS](https://console.aws.amazon.com).
5. Run the database migrations
```shell
$ python3 manage.py migrate
```
6. Start the development server
```shell
$ python3 manage.py collectstatic
$ python3 manage.py runserver
```
