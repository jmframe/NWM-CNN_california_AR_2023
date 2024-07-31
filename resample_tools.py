from typing import Dict, List, Tuple, Union
import affine
import geojson
import numpy as np
import rasterio
from rasterio.crs import CRS
from rasterio.warp import Resampling
from rasterio.vrt import WarpedVRT
def validate_bounds_for_crs(crs: CRS, bounds: Tuple[Union[float, int]]):
    left, bottom, right, top = bounds

    # Sanity check units. Won't catch all mistakes.
    if crs.is_projected:
        # units = metres
        # check that at least one of the bounds is outside of the degree-units range
        assert any(i > 180 or i < -180 for i in bounds), (
            f"It is extremely unlikely that all your bounds are within [-180,+180] for a CRS {crs} with units metres {bounds}. "
            f"Make sure `bounds` are in metres"
        )
    else:
        # units = degrees
        valid_lat = all(-90 <= i <= 90 for i in (top, bottom))
        valid_lon = all(-180 <= i <= 180 for i in (left, right))
        assert (
            valid_lat and valid_lon
        ), f"invalid bounds {bounds} for crs {crs} with units degrees {bounds}. Make sure `bounds` are in degrees"


def warp_image(
    tif_list: List[str],
    dst_bounds: Tuple[float],
    output_dir: str,
    dst_crs: int = 4326,
    dst_height: int = None,
    dst_width: int = None,
    resampling: Resampling = Resampling.nearest,
    src_nodata: Union[float, int] = np.nan,
    dst_nodata: Union[float, int] = np.nan,
    res: Union[float, int] = None,
    band: int = None,
    profile: Dict = None,
    deflate_compression: bool = True,
    save: bool = True,
) -> Union[List[str], str]:
    if not isinstance(tif_list, (list, tuple)):
        tif_list = [tif_list]
    tif_list = [str(i) for i in tif_list]
    dst_crs = CRS.from_user_input(dst_crs)
    validate_bounds_for_crs(dst_crs, dst_bounds)
    profile = {} if not profile else profile

    # Output image transform. Set resolution based on target height/width or resolution if provided
    left, bottom, right, top = dst_bounds
    if res:
        xres = res
        yres = res
        if not dst_height or not dst_width:
            dst_height = round((top - bottom) / yres)
            dst_width = round((right - left) / xres)
    else:
        xres = (right - left) / dst_width
        yres = (top - bottom) / dst_height
    dst_transform = affine.Affine(xres, 0.0, left, 0.0, -1 * yres, top)

    vrt_options = {
        # if you pass `height` or `width` as part of profile, they will be overwritten
        **profile,
        "resampling": resampling,
        "crs": dst_crs,
        "transform": dst_transform,
        # specify height & width to load **only** the roi per image-tile = faster
        "height": dst_height,
        "width": dst_width,
        "src_nodata": src_nodata,
        "nodata": dst_nodata,
    }
    if deflate_compression:
        vrt_options["compress"] = "deflate"
    else:
        vrt_options.pop("compress", None)

    outfiles = []
    for p in tif_list:
        with rasterio.open(p) as src:
            with WarpedVRT(src, **vrt_options) as vrt:
                filename = p.split("/")[-1].replace(
                    ".tif",
                    f".nodata{src_nodata}_{resampling.name}_{dst_height}x{dst_width}_res{yres:.4f}x{xres:.4f}.tif",
                )
                outfile = f"{output_dir}/{filename}"
                if band is not None:
                    data = vrt.read(band)
                else:
                    data = vrt.read(band)

                if save:
                    this_profile = vrt.profile
                    this_profile["driver"] = "GTiff"
                    if band is not None:
                        this_profile["count"] = 1

                    with rasterio.open(outfile, "w", **this_profile) as dst:
                        if band is not None:
                            dst.write(data, 1)
                        else:
                            dst.write(data)
                    outfiles.append(outfile)
    if save:
        if len(outfiles) == 1:
            outfiles = outfiles[0]
        return outfiles
    else:
        return data
def get_geojson_bounds(aoi_geojson):
    if isinstance(aoi_geojson, dict):
        aoi_geojson = geojson.base.GeoJSON(aoi_geojson)
    coords = list(geojson.utils.coords(aoi_geojson))
    lats = [x[1] for x in coords]
    lons = [x[0] for x in coords]
    lat_min, lat_max = min(lats), max(lats)
    lon_min, lon_max = min(lons), max(lons)
    return lat_max, lon_min, lat_min, lon_max