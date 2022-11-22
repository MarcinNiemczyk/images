# How to set up the project

#### 1. Download repository

```
git clone https://github.com/martindustry/images.git
```

#### 2. Run docker compose

```
docker-compose -p marcin_niemczyk up
```

#### 3. Enter localhost

```
127.0.0.1:8000
```

#### Superuser credentials

username: `admin` password: `admin`

#### Default tier for new user: BASIC \*

\* Account Tier can be changed using django-admin UI.

## Endpoints

| Method   | URL                | Description                                              |
| -------- | ------------------ | -------------------------------------------------------- |
| `GET`    | `/api/images`      | List own images and/or thumbnails                        |
| `POST`   | `/api/images`      | Upload an image                                          |
| `GET`    | `/api/images/<id>` | Retrieve single image                                    |
| `PUT`    | `/api/images/<id>` | Update image                                             |
| `DELETE` | `/api/images/<id>` | Delete image                                             |
| `GET`    | `/api/generate`    | List available expiring links (only that aren't expired) |
| `POST`   | `/api/generate`    | Generate expiring link                                   |
| `GET`    | `/api/temp/<uuid>` | View image directly from expiring link                   |

## Tech Stack:

-   Django / REST Framework
-   Docker / Docker-Compose
-   PostgreSQL
-   SQLite (development)

#### Libraries

-   Coverage.py
-   Unittest
