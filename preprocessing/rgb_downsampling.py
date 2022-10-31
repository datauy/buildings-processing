from pathlib import Path

from constants import (
    MDS_INPUT_FILE,
    MDS_OUTPUT_FILE,
    OUTPUT_RASTERS,
    RASTER_SCALE_FACTOR,
)
from utils import save_raster, transform_raster

if __name__ == "__main__":
    Path(OUTPUT_RASTERS).mkdir(parents=True, exist_ok=True)
    original_rgb, trans_rgb, transform = transform_raster(MDS_INPUT_FILE, RASTER_SCALE_FACTOR)
    save_raster(original_rgb, trans_rgb, transform, MDS_OUTPUT_FILE)
    print("Done!")
