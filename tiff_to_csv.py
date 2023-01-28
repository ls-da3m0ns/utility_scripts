#!/usr/bin/env python3
"""
converts a large tiff file into a csv file with pixels as polygons 
and their corresponding values as attributes
also adds h3 index to query each row with 
fast and memory efficient way to convert a tiff file into a csv file
support s3 urls as input and output
"""

from multiprocessing.dummy import Array
import os
from typing import List
import rasterio 
import pandas as pd 
import numpy as np
import boto3
from functools import partial
import logging
import tempfile
from shapely.geometry import Polygon, box
import h3 
import geopandas as gpd 

def run_memory_check() -> None:
    tot_m, used_m, free_m = map(int,
        os.popen('free -t -m').readlines()[-1].split()[1:]
    )

    logging.info("Current Memory usage (total,used,free) ",tot_m, used_m, free_m)

    if free_m < tot_m/5:
        logging.info("Less memory available commiting work and quiting ...")
        exit()

def download_s3_file(url : str) -> None:
    temp_file_path: str = tempfile.mktemp()

    logging.info(f"Downloading file from s3 {url} to temp file ", temp_file_path)

    s3_client = boto3.client('s3')
    bucket_name = url.split("/")[2]
    key = "/".join(url.split("/")[3:])
    fname = key.split("/")[-1]
    s3_client.download_file(bucket_name, key, temp_file_path )
    return temp_file_path

def upload_file_to_s3(file_path : str, url : str) -> None:
    s3_client = boto3.client('s3')
    bucket_name = url.split("/")[2]
    key = "/".join(url.split("/")[3:])
    s3_client.upload_file(file_path, bucket_name, key)

def pixel_cords_to_poly(x: int, y:int, transform) -> Polygon:
    move_x,move_y = transform[0],transform[4]
    x_min, y_max = transform * (x,y)
    x_max = x_min + move_x
    y_min = y_max + move_y
    return box(x_min, y_min, x_max, y_max)

def point_to_h3(point_p, res)-> str :
    return h3.geo_to_h3(point_p.y, point_p.x, res)

def get_raster_data(path : str):
    with rasterio.open(path) as dataset:
        transform = dataset.transform
        masked_data = dataset.read_masks(1)
        data = dataset.read(1)
    valid_vals = np.where(masked_data == 0)
    return transform, valid_vals, data

def process_chunk(x: List, y: List, data, transform,  offset: int, num_to_process: int, out_path:str ) -> None:
    start_idx , end_idx = offset, offset + num_to_process
    end_idx = min(end_idx, len(x))

    x_pixels, y_pixels = x[start_idx:end_idx], y[start_idx:end_idx]
    data_values = data[x_pixels,y_pixels]

    create_poly = partial(pixel_cords_to_poly, transform=transform)

    df = pd.DataFrame({
                "y_pixel": x_pixels,
                "x_pixel": y_pixels,
                "value":data_values}, 
        columns=["value"])

    df["geometry"] = df.apply(lambda row: create_poly(row["x_pixel"], row["y_pixel"]), axis=1)
    geo_df = gpd.GeoDataFrame(df, geometry="geometry")
    geo_df.crs = "EPSG:4326"
    geo_df["polygon_cetroid"] = geo_df.centroid
    geo_df["h3_index_11"] = geo_df["polygon_cetroid"].apply(lambda point_p: point_to_h3(point_p, 11))

    geo_df.to_csv(out_path, mode="a", header=True, index=False)

def tiff_to_csv(tiff_path : str, out_path : str, chunk_size : int = 1000000) -> None:
    if tiff_path.startswith("s3://"):
        tiff_path = download_s3_file(tiff_path)


    if out_path.startswith("s3://"): out_path_ = tempfile.mktemp()
    else: out_path_ = out_path

    logging.info("Starting to process tiff file {} with out path {} ".format(tiff_path, out_path_) )

    transform, valid_vals, data = get_raster_data(tiff_path)
    
    logging.info("Finished reading tiff file with length {} ".format(len(valid_vals[0])) )

    x, y = valid_vals
    num_to_process = chunk_size
    offset = 0
    while offset < len(x):
        logging.info("Processing chunk {} ".format(offset) )
        process_chunk(x, y, data, transform, offset, num_to_process, out_path + str(offset))
        if out_path.startswith("s3://"): upload_file_to_s3(out_path + str(offset), out_path + str(offset))
        
        offset += num_to_process
        run_memory_check()



