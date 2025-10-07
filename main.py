__import__("warnings").filterwarnings("ignore", category=UserWarning, module="sdl2")
import sdl2 as sd, ctypes, numpy as np
from typing import Literal
from time import strftime, localtime

def logger_init(log_path: str = "./latest.log"):
    global _log_path
    _log_path = log_path
    with open(log_path, mode="w+", encoding="utf-8") as log_file:
        log_file.close()
def log(*texts: object,
        level: Literal["TRACE", "DEBUG", "INFO", "WARN", "ERROR", "FATAL"] = "INFO",
        thread: str = "Main") -> str:
    global _log_path
    text = f"[{strftime("%H:%M:%S", localtime())}] [{thread}/{level}]: {" ".join([t.__str__() for t in texts])}"
    with open(_log_path, mode="a+", encoding="utf-8") as log_file:
        log_file.write(text + "\n")
        log_file.close()
    print(text)
    return texts
logger_init()

sdl2_version = sd.SDL_version()
sd.SDL_GetVersion(sdl2_version)
log(f"SDL2 Version: {sdl2_version.major}.{sdl2_version.minor}.{sdl2_version.patch}")

# 获取帧
def get_frame(width: int, height: int) -> np.ndarray:
    arr = np.zeros((height, width, 4), dtype=np.uint8)
    return arr

def main():

    width, height = 768, 512

    # 窗口
    window = sd.SDL_CreateWindow(
        b"Window",
        sd.SDL_WINDOWPOS_CENTERED,
        sd.SDL_WINDOWPOS_CENTERED,
        width, height,
        sd.SDL_WINDOW_SHOWN
    )
    if not window:
        log(f"SDL_CreateWindow Error: {sd.SDL_GetError()}")
        sd.SDL_Quit()
        return 1
    log("窗口创建完毕。")

    # 渲染器
    renderer = sd.SDL_CreateRenderer(
        window,
        -1, 
        sd.SDL_RENDERER_ACCELERATED | sd.SDL_RENDERER_PRESENTVSYNC
    )
    if not renderer:
        log(f"SDL_CreateRenderer Error: {sd.SDL_GetError()}")
        sd.SDL_DestroyWindow(window)
        sd.SDL_Quit()
        return 1
    log("渲染器创建完毕。")

    # 纹理
    texture = sd.SDL_CreateTexture(
        renderer,
        sd.SDL_PIXELFORMAT_RGBA32,
        sd.SDL_TEXTUREACCESS_STREAMING,
        width, height
    )
    if not texture:
        log(f"SDL_CreateTexture Error: {sd.SDL_GetError()}")
        sd.SDL_DestroyRenderer(renderer)
        sd.SDL_DestroyWindow(window)
        sd.SDL_Quit()
        return 1
    log("纹理创建完毕。")

    running: bool = True
    event = sd.SDL_Event()

    while running:
        while sd.SDL_PollEvent(ctypes.byref(event)) != 0:
            if event.type == sd.SDL_QUIT:
                running = False

        # RGBA
        frame = get_frame(width, height)
        # Lock
        pixels = ctypes.c_void_p()
        pitch = ctypes.c_int()
        sd.SDL_LockTexture(texture, None, ctypes.byref(pixels), ctypes.byref(pitch))

        # Copy
        ctypes.memmove(pixels, frame.ctypes.data, width * height * 4)

        # UnLock
        sd.SDL_UnlockTexture(texture)

        sd.SDL_RenderClear(renderer)
        sd.SDL_RenderCopy(renderer, texture, None, None)
        sd.SDL_RenderPresent(renderer)

    # 资源释放
    sd.SDL_DestroyTexture(texture)
    sd.SDL_DestroyRenderer(renderer)
    sd.SDL_DestroyWindow(window)
    sd.SDL_Quit()

    return 0

if __name__ == "__main__":
    log(f"程序停止运行，退出代码：{main()}")