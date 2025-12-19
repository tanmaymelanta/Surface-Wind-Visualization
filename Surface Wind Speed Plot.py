import datetime as dt
from datetime import timedelta
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import matplotlib.colors as mcolors
import imageio
from io import BytesIO
import warnings
warnings.filterwarnings("ignore")

def get_url_base():
    url_string = [
        (dt.date.today()).strftime("%Y%m%d") + "/gfs_0p25_1hr_18z", (dt.date.today()).strftime("%Y%m%d") + "/gfs_0p25_1hr_18z",
        (dt.date.today()).strftime("%Y%m%d") + "/gfs_0p25_1hr_18z", (dt.date.today()).strftime("%Y%m%d") + "/gfs_0p25_1hr_12z",
        (dt.date.today()).strftime("%Y%m%d") + "/gfs_0p25_1hr_18z", (dt.date.today()).strftime("%Y%m%d") + "/gfs_0p25_1hr_06z"
        (dt.date.today()).strftime("%Y%m%d") + "/gfs_0p25_1hr_06z", (dt.date.today()).strftime("%Y%m%d") + "/gfs_0p25_1hr_00z",
        (dt.date.today() - timedelta(days=1)).strftime("%Y%m%d") + "/gfs_0p25_1hr_18z", (dt.date.today() - timedelta(days=1)).strftime("%Y%m%d") + "/gfs_0p25_1hr_18z",
        (dt.date.today() - timedelta(days=1)).strftime("%Y%m%d") + "/gfs_0p25_1hr_18z", (dt.date.today() - timedelta(days=1)).strftime("%Y%m%d") + "/gfs_0p25_1hr_12z",
        (dt.date.today() - timedelta(days=1)).strftime("%Y%m%d") + "/gfs_0p25_1hr_18z", (dt.date.today() - timedelta(days=1)).strftime("%Y%m%d") + "/gfs_0p25_1hr_06z",
        (dt.date.today() - timedelta(days=1)).strftime("%Y%m%d") + "/gfs_0p25_1hr_06z", (dt.date.today() - timedelta(days=1)).strftime("%Y%m%d") + "/gfs_0p25_1hr_00z"
    ]
    for url_base in url_string:
        url = f"https://nomads.ncep.noaa.gov/dods/gfs_0p25_1hr/gfs{url_base}"
        try:
            with xr.open_dataset(url) as ds:
                print(f"Data available for: {url_base}")
                return url_base
        except Exception as e:
            print(f"Error accessing data for {url_base}: {e}")
    print("No data found.")
    return None

def get_dataset(url_base):
    url = f"https://nomads.ncep.noaa.gov/dods/gfs_0p25_1hr/gfs{url_base}"
    with xr.open_dataset(url) as ds:
        return ds

def load_surface_wind_data(time_hour, ds):
    u_var = 'ugrd10m'
    v_var = 'vgrd10m'
    lat = (-90, 90)
    lon = (0, 360)
    time_at_hour = dt.datetime.strptime(str(ds.time.isel(time=time_hour).values).split('.')[0], "%Y-%m-%dT%H:%M:%S").strftime("%b %d, %Y %H")
    u_da = ds[u_var].isel(time=time_hour).sel(lat=slice(*lat), lon=slice(*lon))
    v_da = ds[v_var].isel(time=time_hour).sel(lat=slice(*lat), lon=slice(*lon))
    wind_speed = np.sqrt(u_da ** 2 + v_da ** 2) * 1.944
    wind_speed.name = "wind_speed"
    wind_speed_df = wind_speed.to_dataframe().reset_index()
    wind_speed_df['ugrd10m'] = u_da.values.flatten()
    wind_speed_df['vgrd10m'] = v_da.values.flatten()
    wind_speed_df_pre = wind_speed_df.copy()
    wind_speed_df_pre['lon'] = wind_speed_df_pre['lon'] - 360
    return wind_speed_df_pre, wind_speed_df, time_at_hour

def plot_surface_wind(wind_speed_df_pre, wind_speed_df, time_at_hour, skip=10, min_wind_speed=10):
    fig, ax = plt.subplots(figsize=(7, 3), dpi=300)    
    m = Basemap(projection='cyl', llcrnrlat=-90, urcrnrlat=90, llcrnrlon=-180, urcrnrlon=240, resolution='h', ax=ax)
    m.drawcoastlines(linewidth=0.3)
    m.drawparallels(np.arange(-90., 91., 30.), labels=[1, 0, 0, 0], fontsize=4, linewidth=0.5)
    m.drawmeridians(np.arange(0., 361., 60.), labels=[0, 0, 0, 1], fontsize=4, linewidth=0.5)

    colors = ['#FFFFFF', '#E2EBF5', '#A7C2E0', '#6C99D1', '#33CC99', '#6AFF6A', '#FFE600', '#FF9600', '#FA3C3C', '#C80000', '#CC00CC']
    bounds = [round(wind_speed_df['wind_speed'].min()), 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, round(wind_speed_df['wind_speed'].max())]
    cmap = mcolors.ListedColormap(colors)
    norm = mcolors.BoundaryNorm(bounds, cmap.N)
    
    unique_lats = np.unique(wind_speed_df['lat'])
    unique_lons = np.unique(wind_speed_df['lon'])
    wind_speed = wind_speed_df['wind_speed'].values.reshape(len(unique_lats), len(unique_lons))
    u_comp = wind_speed_df['ugrd10m'].values.reshape(len(unique_lats), len(unique_lons))
    v_comp = wind_speed_df['vgrd10m'].values.reshape(len(unique_lats), len(unique_lons))

    lon2d, lat2d = np.meshgrid(unique_lons, unique_lats)
    x, y = m(lon2d, lat2d)
    cs = m.pcolormesh(x, y, wind_speed, cmap=cmap, norm=norm, shading='auto')
    cbar = m.colorbar(cs, location='bottom', pad="8%", ticks=bounds, shrink=10, aspect=100)
    cbar.ax.set_xticklabels([str(b) for b in bounds], fontsize=3)
    
    mask = wind_speed >= min_wind_speed
    u_comp_masked = np.ma.masked_where(~mask, u_comp)
    v_comp_masked = np.ma.masked_where(~mask, v_comp)
    x_masked = np.ma.masked_where(~mask, x)
    y_masked = np.ma.masked_where(~mask, y)
    m.barbs(x_masked[::skip, ::skip], y_masked[::skip, ::skip], u_comp_masked[::skip, ::skip], v_comp_masked[::skip, ::skip], length=2, linewidth=0.1, color='k', pivot='middle')
    
    unique_lats_pre = np.unique(wind_speed_df_pre['lat'])
    unique_lons_pre = np.unique(wind_speed_df_pre['lon'])
    wind_speed_pre = wind_speed_df_pre['wind_speed'].values.reshape(len(unique_lats_pre), len(unique_lons_pre))
    u_comp_pre = wind_speed_df_pre['ugrd10m'].values.reshape(len(unique_lats_pre), len(unique_lons_pre))
    v_comp_pre = wind_speed_df_pre['vgrd10m'].values.reshape(len(unique_lats_pre), len(unique_lons_pre))
    
    lon2d_pre, lat2d_pre = np.meshgrid(unique_lons_pre, unique_lats_pre)
    x_pre, y_pre = m(lon2d_pre, lat2d_pre)
    cs_pre = m.pcolormesh(x_pre, y_pre, wind_speed_pre, cmap=cmap, norm=norm, shading='auto')
    cbar_pre = m.colorbar(cs_pre, location='bottom', pad="8%", ticks=bounds, shrink=10, aspect=100)
    cbar_pre.ax.set_xticklabels([str(b) for b in bounds], fontsize=3)
    
    mask_pre = wind_speed_pre >= min_wind_speed
    u_comp_masked_pre = np.ma.masked_where(~mask_pre, u_comp_pre)
    v_comp_masked_pre = np.ma.masked_where(~mask_pre, v_comp_pre)
    x_masked_pre = np.ma.masked_where(~mask_pre, x_pre)
    y_masked_pre = np.ma.masked_where(~mask_pre, y_pre)
    m.barbs(x_masked_pre[::skip, ::skip], y_masked_pre[::skip, ::skip], u_comp_masked_pre[::skip, ::skip], v_comp_masked_pre[::skip, ::skip], length=2, linewidth=0.1, color='k', pivot='middle')
    ax.set_title(f'Surface Wind Speed (knots) on {time_at_hour} UTC', fontsize=10)
    return fig

def main():
    url_base = get_url_base()
    ds = get_dataset(url_base)
    if url_base:
        with imageio.get_writer(r"C:\Users\surface_wind_speed.gif", mode='I', duration=1000) as writer:
            for i in range(0, 73, 3):
                try:
                    time_hour = i
                    wind_speed_df_pre, wind_speed_df, time_at_hour = load_surface_wind_data(time_hour, ds)
                    fig = plot_surface_wind(wind_speed_df_pre, wind_speed_df, time_at_hour)
                    buf = BytesIO()
                    fig.savefig(buf, format='png')
                    buf.seek(0)
                    image = imageio.imread(buf)
                    writer.append_data(image)
                    plt.close(fig)
                except Exception as e:
                    print(f"Error processing report {i}: {e}")
                    continue

if __name__ == "__main__":
    main()
