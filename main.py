from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from contextlib import asynccontextmanager
import ldclient
from ldclient import Context
from ldclient.config import Config
import os

# Add this new function to instantiate and shut down the LaunchDarkly client
@asynccontextmanager
async def lifespan(app: FastAPI):
  # initialize the LaunchDarkly SDK
  ld_sdk_key = os.getenv("LAUNCHDARKLY_SDK_KEY")
  ldclient.set_config(Config(ld_sdk_key))
  yield
  # Shut down the connection to the LaunchDarkly client
  ldclient.get().close()

# Add the new lifespan parameter
app = FastAPI(lifespan=lifespan)

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
   context = Context.builder("context-key-123abc").set("email", "sandy@example.edu").build()
   show_student_version = ldclient.get().variation("show-student-version", context, False)
   file_name = "static/index.html"
   if show_student_version == True:
      file_name = "static/student-index.html"
   return FileResponse(file_name)