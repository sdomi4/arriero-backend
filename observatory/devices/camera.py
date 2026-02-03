from observatory.devices.base import ObservatoryDevice
from arriero.arriero import Arriero
from alpaca import camera
from observatory.errors import CameraError
from time import sleep
import time
from typing import TYPE_CHECKING, Callable
import asyncio
import numpy as np
import astropy.io.fits as fits

if TYPE_CHECKING:
    from observatory.observatory import Observatory

class ArrieroCamera(ObservatoryDevice[camera.Camera]):
    def __init__(self, observatory: "Observatory", factory: Callable[[], camera.Camera], updater: Callable[[], None], id: str, name: str = None, poll_time: float = 1):
        arriero = Arriero(
            factory,
            updater,
            poll_time=poll_time,
            name=name or id,
        )
        super().__init__(observatory, arriero, id=id, name=name)

    def cool(self, target_temp: float):
        try:
            if not self.alpaca.CoolerOn:
                self.alpaca.CoolerOn = True
            self.alpaca.SetCCDTemperature = target_temp
        except Exception as e:
            raise CameraError(code="camera_cool_failed", message=f"Error setting camera {self.arriero.name} temperature: {e}")

    def wait_for_temperature(self, timeout: int = 600):
        try:
            if not self.alpaca.CoolerOn:
                raise CameraError(code="cooler_not_on", message=f"Camera {self.arriero.name} cooler is not on")
            
            start_time = time.time()
            while True:
                current_temp = self.alpaca.CCDTemperature
                target_temp = self.alpaca.SetCCDTemperature
                self.observatory.state.add_action(f"Cooling {self.arriero.name}: {current_temp:.1f}C / {target_temp:.1f}C")
                
                if abs(current_temp - target_temp) < 1:
                    self.observatory.state.remove_action(f"Cooling {self.arriero.name}: {current_temp:.1f}C / {target_temp:.1f}C")
                    return
                
                if time.time() - start_time > timeout:
                    self.observatory.state.remove_action(f"Cooling {self.arriero.name}: {current_temp:.1f}C / {target_temp:.1f}C")
                    raise CameraError(code="camera_cooling_timeout", message=f"Timeout waiting for camera {self.arriero.name} to reach target temperature")
                
                sleep(10)
        except Exception as e:
            raise CameraError(code="camera_temperature_wait_failed", message=f"Error waiting for camera {self.arriero.name} temperature: {e}")

    def expose(self, exposure: float, binX: int = 1, binY: int = 1, startX: int = 0, startY: int = 0):
        try:
            self.alpaca.BinX = binX
            self.alpaca.BinY = binY
            self.alpaca.StartX = startX
            self.alpaca.StartY = startY
            self.alpaca.NumX = self.alpaca.CameraXSize // self.alpaca.BinX
            self.alpaca.NumY = self.alpaca.CameraYSize // self.alpaca.BinY

            self.alpaca.StartExposure(exposure, True)

            while not self.alpaca.ImageReady:
                sleep(0.5)
            
            img = self.alpaca.ImageArray
            imginfo = self.alpaca.ImageArrayInfo

            from alpaca.camera import ImageArrayElementTypes
            if imginfo.ImageElementType == ImageArrayElementTypes.Int32:
                if self.alpaca.MaxADU <= 65535:
                    imgDataType = np.uint16
                else:
                    imgDataType = np.int32
            elif imginfo.ImageElementType == ImageArrayElementTypes.Double:
                imgDataType = np.float64
            else:
                imgDataType = np.uint16

            if imginfo.Rank == 2:
                nda = np.array(img, dtype=imgDataType).transpose()
            else:
                nda = np.array(img, dtype=imgDataType).transpose(2, 1, 0)

            hdr = fits.Header()
            if imgDataType == np.uint16:
                hdr['BZERO'] = 32768.0
                hdr['BSCALE'] = 1.0
            hdr['EXPOSURE'] = exposure
            hdr['EXPTIME'] = exposure
            hdr['DATE-OBS'] = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())
            hdr['TIMESYS'] = 'UTC'
            hdr['XBINNING'] = self.alpaca.BinX
            hdr['YBINNING'] = self.alpaca.BinY
            hdr['INSTRUME'] = self.name
            try:
                hdr['GAIN'] = self.alpaca.Gain
            except:
                pass
            try:
                hdr['OFFSET'] = self.alpaca.Offset
                if type(self.alpaca.Offset) == int:
                    hdr['PEDESTAL'] = self.alpaca.Offset
            except:
                pass
            hdr['HISTORY'] = 'Created using Python alpyca-client library'

            return nda, hdr
        except Exception as e:
            raise CameraError(code="camera_expose_failed", message=f"Error exposing with camera {self.arriero.name}: {e}")

    def create_fits(self, nda, hdr, additional_headers: dict, base_path: str):
        try:
            for k, v in additional_headers.items():
                hdr[k] = v

            hdu = fits.PrimaryHDU(nda, header=hdr)
            filename = f"{base_path}/{hdr['INSTRUME']}_{time.strftime('%Y%m%d_%H%M%S', time.gmtime())}.fits"
            hdu.writeto(filename, overwrite=True)
            return filename
        except Exception as e:
            raise CameraError(code="fits_creation_failed", message=f"Error creating FITS file for camera {self.arriero.name}: {e}")

    async def trigger_expose_and_save(self, exposure: float, base_path: str, binX: int = 1, binY: int = 1, additional_headers: dict = None):
        loop = asyncio.get_event_loop()
        nda, hdr = await loop.run_in_executor(None, lambda: self.expose(exposure, binX, binY))
        filename = await loop.run_in_executor(None, lambda: self.create_fits(nda, hdr, additional_headers or {}, base_path))
        return filename
