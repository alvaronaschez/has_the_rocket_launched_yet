from abc import ABC, abstractmethod
from typing import Union, BinaryIO
from urllib.parse import quote

import httpx


class SequenceOfFrames(ABC):
    @abstractmethod
    def __getitem__(self, key: int) -> Union[str, BinaryIO]:
        """
        Photo to send. Pass a file_id as String to send a photo
        that exists on the Telegram servers (recommended),
        pass an HTTP URL as a String for Telegram to get a photo from the
        Internet, or upload a new photo using multipart/form-data.
        """
        pass

    @abstractmethod
    def __len__(self) -> int:
        pass


class FrameX(SequenceOfFrames):
    api_domain = "framex-dev.wadrid.net"
    video_name = quote("Falcon Heavy Test Flight (Hosted Webcast)-wbSwFU6tY1c")

    def __init__(self, video_name=None):
        if video_name:
            self.video_name = quote(video_name)
        self.length = None

    def __getitem__(self, key: int) -> str:
        url = f"https://{self.api_domain}/api/video/{self.video_name}/frame/{key}/"  # noqa
        return url

    def __len__(self) -> int:
        # the computation is expensive, so lets do it only once
        if self.length is None:
            url = f"https://{self.api_domain}/api/video/{self.video_name}"
            response = httpx.get(url)
            self.length = response.json()["frames"]
        return self.length


frames = FrameX()
frame = frames[1695]
print(frame)
