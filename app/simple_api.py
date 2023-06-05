import io
from os import getenv
from typing import Annotated

import matplotlib.pyplot as plt
import numpy as np
import rasterio
import uvicorn
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Response, UploadFile
from PIL import Image
from utils import brighten, normalize

# Load env variables from `.env`.
load_dotenv()

# Define app paths.
ATTRIBUTES_PATH = '/attributes/'
THUMBNAILS_PATH = '/thumbnails/'
NDVI_PATH = '/ndvi/'

# App handler.
app = FastAPI(title='EarthPulse simple API', description='Satellite image reader and converter.')


async def check_token(csrf_token: str) -> bool:
    """Utility function to check CSRF validity against an environment predefined constant."""
    if str(csrf_token) != getenv('VALID_CSRF_TOKEN'):
        raise HTTPException(status_code=403, detail='Unauthorised. Invalid CSRF Token.')

    return True

async def open_input_image(image: UploadFile) -> rasterio.io.DatasetReader:
    """Ensure the uploaded file can be opened as a raster image.

    If successful, it returns the rasterio object, it raises an error otherwise.
    """
    try:
        return rasterio.open(image.file)
    except Exception as exc:
        raise HTTPException(status_code=400, detail='Malformed. Could not open image.') from exc


@app.post(ATTRIBUTES_PATH)
async def attributes(csrf_token: Annotated[str, Depends(check_token)],  # pylint: disable=W0613
                     image: UploadFile) -> Response:
    """Opens a received image and returns some basic metadata."""
    # Read input file.
    raster = await open_input_image(image)

    # Extract metadata and return output.
    bounds = {
        'left': raster.bounds.left,
        'bottom': raster.bounds.bottom,
        'right': raster.bounds.right,
        'top': raster.bounds.top,
    }

    return {'width': raster.width,
            'height': raster.height,
            'bands': raster.count,
            'crs': raster.crs.to_string(),
            'bounds': bounds,}

@app.post(THUMBNAILS_PATH)
async def thumbnailer(csrf_token: Annotated[str, Depends(check_token)],  # pylint: disable=W0613
                      image: UploadFile) -> Response:
    """Opens a received image and generates a thumbnail.

    It normalises each RGB band. Output size is hardcoded for now.
    """
    # Read input file.
    raster = await open_input_image(image)

    # Convert to RGB.
    red = normalize(brighten(raster.read(4)))
    green = normalize(brighten(raster.read(3)))
    blue = normalize(brighten(raster.read(2)))

    rgb = np.dstack((red, green, blue))
    img = Image.fromarray(np.uint8(rgb*255.999))

    # Resize and write to png (io).
    # This will loose its proportions from WSG84 crs. It should be enough for now.
    img = img.resize((256,256))

    with io.BytesIO() as output:
        img.save(output, format='PNG')
        return Response(output.getvalue(), media_type='image/png')

@app.post(NDVI_PATH)
async def ndvi(csrf_token: Annotated[str, Depends(check_token)],  # pylint: disable=W0613
               image: UploadFile) -> Response:
    """Returns a computed NDVI out of an uploaded image.

    In order to render the output image with a channel map, Matplotlib will be used. This is not ideal as the
    render works towards a virtual paper sheet medium using a GUI utility. Usually that utility would add some
    borders to the generated image, but this has been avoided with some extra steps.
    """
    # Read input file.
    raster = await open_input_image(image)

    red = normalize(raster.read(4))
    nir = normalize(raster.read(8))
    ndvi_array = (nir - red) / (nir + red)

    output_buffer = io.BytesIO()

    # Render image to maplotlib (IDK other ways to set a cmap, right now) and save file to bytes. Remove borders.
    figure = plt.figure(frameon=False)
    figure.set_size_inches(5.12, 5.12)  # With 200 dpi, this makes 1024x1024 images.
    axes = plt.Axes(figure, [0., 0., 1., 1.])
    axes.set_axis_off()
    figure.add_axes(axes)

    axes.imshow(ndvi_array, cmap='RdYlGn', aspect='auto')
    figure.savefig(output_buffer, format='png', dpi=200)
    plt.close(figure)

    output_buffer.seek(0)
    return Response(output_buffer.getvalue(), media_type='image/png')

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=80)
