from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import uuid
import aiofiles

from enhance_service import EnhanceServices


app = FastAPI()

SAVE_DIR = os.getenv("SAVE_DIR", "unprocessed_videos")
PROCESSED_DIR = os.getenv("PROCESSED_DIR", "processed_videos")
os.makedirs(SAVE_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

app.mount("/files", StaticFiles(directory=PROCESSED_DIR), name="files")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/files")
def list_files():
    try:
        files = [
            f for f in os.listdir(PROCESSED_DIR)
            if os.path.isfile(os.path.join(PROCESSED_DIR, f))
        ]
        return JSONResponse(content={"files": files})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get('remove_file/{file_full_name}')
def remove_file(file_full_name: str):
    try:
        file_path = os.path.join(PROCESSED_DIR, file_full_name)

        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")

        os.remove(file_path)
        return JSONResponse(content={"message": f"{file_full_name} removed successfully"})

    except:
        return JSONResponse(status_code=500, content={"error": "Something went wrong"})


@app.post("/enhance_video")
async def enhance_video_multipart(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    try:
        # Normalize filename
        base = file.filename or f"{uuid.uuid4()}.mp4"
        if not base.lower().endswith(".mp4"):
            base += ".mp4"

        out_path = os.path.join(SAVE_DIR, base)

        # Stream to disk (1 MB chunks)
        async with aiofiles.open(out_path, "wb") as f:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                await f.write(chunk)

        await file.close()

        en = EnhanceServices()
        background_tasks.add_task(en.enhance_video, out_path)

        return JSONResponse(
            status_code=201,
            content={"filename": base, "path": out_path}
        )

    except Exception as e:
        # Optional: clean up partial file
        try:
            if "out_path" in locals() and os.path.exists(out_path):
                os.remove(out_path)
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=str(e))


def main():

    # This runs uvicorn programmatically
    uvicorn.run("main:app", host="127.0.0.1", port=5055, reload=True)

if __name__ == "__main__":
    main()