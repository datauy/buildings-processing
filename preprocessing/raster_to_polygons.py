# %%
from pathlib import Path

import rasterio
from constants import MDT_INPUT_FILE, OUTPUT_VECTORS
from rasterio import features
from utils import mask_raster_band_by_value, raster_to_polygons

# %%
if __name__ == "__main__":
    raster = rasterio.open(MDT_INPUT_FILE)
    # Set mask based on no-data values
    raster_no_data_value = raster.read(1).min()
    mdt_masked_raster = mask_raster_band_by_value(
        raster_band=raster.read(1), no_data_value=raster_no_data_value
    )
    # Get polygon and value from each raster cell:
    masked_raster_polygons = features.shapes(mdt_masked_raster)
    # Convert to polygons
    masked_polygons_gdf = raster_to_polygons(
        shapes_from_raster=masked_raster_polygons, parallel=True
    )
    # Write geodataframe
    filename = Path(MDT_INPUT_FILE).name
    output_file = Path(OUTPUT_VECTORS) / f"{filename}.geojson"
    print(f"Saving output to {output_file}")
    Path(OUTPUT_VECTORS).mkdir(parents=True, exist_ok=True)
    masked_polygons_gdf.to_file(output_file, driver="GeoJSON")
    print("Done!")
