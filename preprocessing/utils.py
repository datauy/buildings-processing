from typing import Dict, Generator, List, Tuple

import affine
import geopandas as gpd
import numpy as np
import rasterio
from constants import CRS_EPSG, NUM_PARALLEL_JOBS
from joblib import Parallel, delayed
from rasterio.enums import Resampling
from shapely.geometry import Polygon


def normalize(x: np.array, lower: int, upper: int):
    """Normalize an array to a given bound interval"""
    print(f"Normalizing raster values to {lower}-{upper} range")
    x_max = np.max(x)
    x_min = np.min(x)
    m = (upper - lower) / (x_max - x_min)
    x_norm = (m * (x - x_min)) + lower
    return x_norm


def transform_raster(input_file: str, scale_factor: float):
    print(f"Scaling raster {input_file}")
    with rasterio.open(input_file) as original_rgb:
        # Resample data to target shape
        trans_rgb = original_rgb.read(
            out_shape=(
                original_rgb.count,
                int(original_rgb.height * scale_factor),
                int(original_rgb.width * scale_factor),
            ),
            resampling=Resampling.bilinear,
        )

        # Scale image transform
        transform = original_rgb.transform * original_rgb.transform.scale(
            (original_rgb.width / trans_rgb.shape[-1]), (original_rgb.height / trans_rgb.shape[-2])
        )
        return original_rgb, trans_rgb, transform


def save_raster(
    original_rgb: rasterio.DatasetReader, trans_rgb: np.array, transform: affine.Affine, output: str
):
    print(f"Saving raster to {output}")
    dst_kwargs = original_rgb.meta.copy()
    dst_kwargs.update(
        {
            "transform": transform,
            "width": trans_rgb.shape[-1],
            "height": trans_rgb.shape[-2],
            "count": trans_rgb.shape[0] - 1,
        }
    )

    with rasterio.open(output, "w", **dst_kwargs) as dst:
        for i in range(trans_rgb.shape[0] - 1):
            dst.write(normalize(trans_rgb[i], 0, 255).astype(rasterio.uint8), i + 1)


def mask_raster_band_by_value(raster_band: np.ndarray, no_data_value: float):
    masked_raster_band = np.ma.masked_array(raster_band, mask=(raster_band == no_data_value))
    return masked_raster_band


def calculate_ndvi(input_rgbi_raster_file: str, output_file: str = None):
    rgbi_raster = rasterio.open(input_rgbi_raster_file)

    # Get red band
    band_red = rgbi_raster.read(1)

    # Get NIR band
    band_nir = rgbi_raster.read(4)

    # Allow division by zero
    np.seterr(divide="ignore", invalid="ignore")

    # Calculate NDVI
    ndvi_band = (band_nir - band_red) / (band_nir + band_red)

    # Set pixels whose values are outside the NDVI range (-1, 1) to NaN
    ndvi_band[ndvi_band > 1] = np.nan
    ndvi_band[ndvi_band < -1] = np.nan

    if output_file:
        dst_kwargs = rgbi_raster.meta.copy()
        dst_kwargs.update({"count": 1, "dtype": np.float64, "nodata": np.nan})
        with rasterio.open(output_file, "w", **dst_kwargs) as dst:
            dst.write(ndvi_band, 1)

    return ndvi_band


def build_geodataframe_inputs(
    coordinates: List[Tuple[int, int]], cell_value: int
) -> Dict[int, Polygon]:
    dict = {"cell_value": [cell_value], "geometry": [Polygon(coordinates)]}
    return dict


def raster_to_polygons(shapes_from_raster: Generator, parallel: bool = True) -> gpd.GeoDataFrame:

    if parallel:
        print("Running raster to polygons in parallel to speed up the process")
        polygons_dicts = Parallel(n_jobs=NUM_PARALLEL_JOBS, backend="loky")(
            [
                delayed(build_geodataframe_inputs)(polygon.get("coordinates")[0], value)
                for polygon, value in shapes_from_raster
            ]
        )
    else:
        print("Running raster to polygons sequentially, it could take some time...")
        polygons_dicts = []
        for polygon, value in shapes_from_raster:
            polygons_dicts.append(build_geodataframe_inputs(polygon.get("coordinates")[0], value))

    polygons_dict_gdf = {"cell_value": [], "geometry": []}

    for poly in polygons_dicts:
        cell_value, geometry = poly.get("cell_value")[0], poly.get("geometry")[0]
        polygons_dict_gdf["cell_value"].append(cell_value)
        polygons_dict_gdf["geometry"].append(geometry)

    return gpd.GeoDataFrame(data=polygons_dict_gdf, crs=CRS_EPSG)
