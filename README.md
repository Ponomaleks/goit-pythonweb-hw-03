# Python Web App

Simple HTTP web app with Jinja2 templates.

## Run Locally (Pipenv)

1. Install dependencies:

```bash
pipenv install
```

2. Start the app:

```bash
pipenv run python main.py
```

3. Open in browser:

```text
http://localhost:3000
```

## Run with Docker

1. Build image:

```bash
docker build -t goit-pythonweb-hw-03 .
```

2. Start container with persistent named volume:

```bash
docker run --rm -p 3000:3000 -v goit_data:/data goit-pythonweb-hw-03
```

3. Open in browser:

```text
http://localhost:3000
```

## Data Persistence

- The app stores messages in `data.json`.
- In Docker mode, the file is written to `/data/data.json`.
- Because `/data` is mounted as a volume, data remains after container restarts.
