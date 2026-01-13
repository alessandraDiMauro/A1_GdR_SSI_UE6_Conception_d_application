# SI Barrage

This project is a FastAPI application.

## Setup and Run

This project uses `uv` for environment and package management.

### 1. Install `uv`

If you don't have `uv` installed, you can install it with:

```shell
# macOS & Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
irm https://astral.sh/uv/install.ps1 | iex
```

### 2. Create the Virtual Environment and Install Dependencies

From the `si_barrage` directory, create a new virtual environment.

```shell
uv sync
```

### 4. Run the Application

To run the FastAPI server, execute the following command from the project's root directory:

```shell
uvicorn si_barrage.main:app --reload
```

The application will be available at `http://127.0.0.1:8000`.
The auto-generated API documentation can be accessed at `http://127.0.0.1:8000/docs`.
