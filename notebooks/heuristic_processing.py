# %%
import numpy as np
import rasterio
from rasterio.plot import show

from preprocessing.utils import calculate_ndvi, mask_raster_band_by_value

MDS_INPUT_FILE = "data/ideuy/K29D6P6_MDS_Remesa_01_MVD.tif"
MDT_INPUT_FILE = "data/ideuy/K29D6P6_MDT_Remesa_01_MVD.tif"
RGBI_INPUT_FILE = "data/ideuy/K29D6P6_RGBI_16_Remesa_01_MVD.tif"
NDVI_OUTPUT_FILE = "data/ideuy/K29D6P6_NDVI_16_Remesa_01_MVD.tif"
DIFF_OUTPUT_FILE = "data/ideuy/K29D6P6_MVD_diff.tif"

# %%
# Read data
mds_raster = rasterio.open(MDS_INPUT_FILE)
mdt_raster = rasterio.open(MDT_INPUT_FILE)
rgbi_raster = rasterio.open(RGBI_INPUT_FILE)

# %%
# Plot rasters
show(mds_raster)
show(mdt_raster)
show(rgbi_raster)

# %%
# Raster operations: MDS - MDT

# Mask no-data values (value == -32767.0)
mds_no_data_value = mds_raster.read(1).min()
mdt_no_data_value = mdt_raster.read(1).min()

mds_masked_raster = mask_raster_band_by_value(
    raster_band=mds_raster.read(1), no_data_value=mds_no_data_value
)
mdt_masked_raster = mask_raster_band_by_value(
    raster_band=mdt_raster.read(1), no_data_value=mdt_no_data_value
)

# diff_raster = mds_masked_raster - mdt_masked_raster

# %%

# Calculate NDVI
ndvi_raster = calculate_ndvi(input_rgbi_raster_file=RGBI_INPUT_FILE, output_file=NDVI_OUTPUT_FILE)

# Plot raster
show(ndvi_raster)

# %%
