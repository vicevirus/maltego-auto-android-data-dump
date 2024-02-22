from maltego_trx.entities import GPS
from maltego_trx.maltego import UIM_TYPES
from maltego_trx.transform import DiscoverableTransform
import piexif
from PIL import Image
import os

class ImageGPSDumper(DiscoverableTransform):
    """
    A Maltego transform to extract GPS coordinates from images in a specified directory.
    """
    @classmethod
    def create_entities(cls, request, response):
        dataDir = request.Value

        try:
            image_gps = cls.get_image_gps(
                os.path.join(dataDir, "media", "0", "DCIM"))
            for gps in image_gps:
                gps_entity = response.addEntity(
                    GPS, f"{gps['GPSLatitude']}, {gps['GPSLongitude']}")
                gps_entity.addProperty(
                    fieldName="lat", displayName="Latitude", value=gps['GPSLatitude'])
                gps_entity.addProperty(
                    fieldName="long", displayName="Longitude", value=gps['GPSLongitude'])
                gps_entity.addProperty(
                    fieldName="filename", displayName="File Name", value=gps['FileName'])
                # Use a property to indicate the category
                gps_entity.addProperty(
                    fieldName="category", displayName="Category", value="GPS")
        except Exception as e:
            response.addUIMessage(
                "Failed to extract GPS from images: " + str(e), UIM_TYPES["partial"])

    @staticmethod
    def get_image_gps(DCIMFolderPath: str):
        codec = 'latin-1'
        gpsData = []
        def convertTupleToFloat(x): return x[0]/x[1]

        def combinePosition(x): return convertTupleToFloat(
            x[0])+(convertTupleToFloat(x[1])/60)+(convertTupleToFloat(x[2])/3600)

        for path, _, files in os.walk(DCIMFolderPath):
            for fileName in files:
                try:
                    fullFilePath = os.path.join(path, fileName)
                    img = Image.open(fullFilePath)
                    exifDict = piexif.load(img.info["exif"])
                    exifTagDict = {}
                    thumbnail = exifDict.pop('thumbnail')
                    exifTagDict['thumbnail'] = thumbnail.decode(codec)
                    for ifd in exifDict:
                        exifTagDict[ifd] = {}
                        for tag in exifDict[ifd]:
                            try:
                                e = exifDict[ifd][tag].decode(codec)
                            except AttributeError:
                                e = exifDict[ifd][tag]
                            exifTagDict[ifd][piexif.TAGS[ifd][tag]["name"]] = e
                    gps = exifTagDict['GPS']
                    gpsData.append({
                        "FullPath": fullFilePath,
                        "FileName": fileName,
                        "GPSLatitude": combinePosition(gps["GPSLatitude"])*((-1) if gps["GPSLatitudeRef"] == "S" else 1),
                        "GPSLongitude": combinePosition(gps["GPSLongitude"])*((-1) if gps["GPSLongitudeRef"] == "W" else 1),
                    })
                except:
                    pass
        return gpsData

