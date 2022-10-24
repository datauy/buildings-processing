from utils import save_raster, transform_raster

SCALE_FACTOR = 1 / 4
INPUT_FILE = "../data/ideuy/K29D6P6_MDS_Remesa_01_MVD.tif"
OUTPUT_FILE = "../data/ideuy/K29D6P6_MDS_MVD_025x.tif"

if __name__ == "__main__":
    original_rgb, trans_rgb, transform = transform_raster(INPUT_FILE, SCALE_FACTOR)
    save_raster(original_rgb, trans_rgb, transform, OUTPUT_FILE)
