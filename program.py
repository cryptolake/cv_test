from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse
from typing_extensions import Annotated
import cv2
import numpy as np
from numpy.linalg import norm
import bisect
import multiprocess as mp

app = FastAPI()

p_manager = mp.Manager()
p_process = None
p_frames = p_manager.list([])

def read_video_stream(frames, rtsp_url):
    capture = cv2.VideoCapture(rtsp_url)
    def brightness(img):
        return np.average(norm(img, axis=2)) / np.sqrt(3)

    while True:
        ret, frame = capture.read()
        if not ret:
            break
        frame = cv2.resize(frame, dsize=(300, 300))
        # insert and sort frame from most bright to least bright
        frames.append(frame)
        frames.sort(key=brightness, reverse=True)
        del frames[9:]


@app.post("/start", response_class=JSONResponse)
async def start(rtsp_url: Annotated[str, Form()]):
    global p_process, p_frames

    p_frames = p_manager.list([])
    p_process = mp.Process(target=read_video_stream,args=(p_frames, rtsp_url))
    p_process.start()
    
    return {"message": "Video stream started."}

@app.get("/stop", response_class=HTMLResponse)
async def stop():
    import itertools
    import base64
    global p_process, p_frames

    if p_process is None:
        return "<div>No video stream is running.</div>"

    p_process.kill()
    p_process = None
    if not p_frames:
        return "<div>Frames were not processed</div>"

    # Turn the 9 images into grid
    frames = p_frames[:9] #make sure no more than 9 frames in list
    w = 3
    h = 3
    img_h, img_w, img_c = frames[0].shape
    mat_x = img_w * w
    mat_y = img_h * h
    grid_image = np.zeros((mat_y, mat_x, img_c), dtype=np.uint)

    img_positions = itertools.product(range(h), range(w))

    for (y_i, x_i), img in zip(img_positions, frames):
        x = x_i * img_w
        y = y_i * img_h

        grid_image[y:y+img_h, x:x+img_w, :] = img

    # Encode image into base64 to display in html
    _, grid_image = cv2.imencode('.jpg', grid_image)
    grid_image_enc = base64.b64encode(grid_image)

    p_frames = p_manager.list([]) 
    return f"""
    <div>
        <img src="data:image/jpg;base64, {str(grid_image_enc, encoding='ascii')}" />
    </div>

    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
