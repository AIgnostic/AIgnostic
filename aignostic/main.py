from aignostic import create_application
import uvicorn

app = create_application()
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
