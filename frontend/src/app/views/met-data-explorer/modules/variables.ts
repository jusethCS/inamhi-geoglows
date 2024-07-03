export class DataVariables {

  public satelliteProducts = [
    { Variable: 'Precipitación', Producto: 'CHIRPS', Temporalidad: 'Diaria' },
    { Variable: 'Precipitación', Producto: 'CHIRPS', Temporalidad: 'Mensual' },
    { Variable: 'Precipitación', Producto: 'CHIRPS', Temporalidad: 'Anual' },
    { Variable: 'Precipitación', Producto: 'CMORPH', Temporalidad: 'Diaria' },
    { Variable: 'Precipitación', Producto: 'CMORPH', Temporalidad: 'Mensual' },
    { Variable: 'Precipitación', Producto: 'CMORPH', Temporalidad: 'Anual' },
    { Variable: 'Precipitación', Producto: 'PERSIANN', Temporalidad: 'Diaria' },
    { Variable: 'Precipitación', Producto: 'PERSIANN', Temporalidad: 'Mensual' },
    { Variable: 'Precipitación', Producto: 'PERSIANN', Temporalidad: 'Anual' },
    { Variable: 'Precipitación', Producto: 'PERSIANN-CCS', Temporalidad: 'Diaria' },
    { Variable: 'Precipitación', Producto: 'PERSIANN-CCS', Temporalidad: 'Mensual' },
    { Variable: 'Precipitación', Producto: 'PERSIANN-CCS', Temporalidad: 'Anual' },
    { Variable: 'Precipitación', Producto: 'PERSIANN-PDIR', Temporalidad: 'Diaria' },
    { Variable: 'Precipitación', Producto: 'PERSIANN-PDIR', Temporalidad: 'Mensual' },
    { Variable: 'Precipitación', Producto: 'PERSIANN-PDIR', Temporalidad: 'Anual' },
    { Variable: 'Precipitación', Producto: 'IMERG', Temporalidad: 'Diaria' },
    { Variable: 'Precipitación', Producto: 'IMERG', Temporalidad: 'Mensual' },
    { Variable: 'Precipitación', Producto: 'IMERG', Temporalidad: 'Anual' },
    { Variable: 'Precipitación', Producto: 'IMERG-EARLY', Temporalidad: 'Diaria' },
    { Variable: 'Precipitación', Producto: 'IMERG-EARLY', Temporalidad: 'Mensual' },
    { Variable: 'Precipitación', Producto: 'IMERG-EARLY', Temporalidad: 'Anual' },
    { Variable: 'Precipitación', Producto: 'IMERG-LATE', Temporalidad: 'Diaria' },
    { Variable: 'Precipitación', Producto: 'IMERG-LATE', Temporalidad: 'Mensual' },
    { Variable: 'Precipitación', Producto: 'IMERG-LATE', Temporalidad: 'Anual' }
  ]

  public forecastProducts = [
    {Model: "WRF", Variable: "Precipitación", Code: "wrf-pacum"},
    {Model: "WRF", Variable: "Temperatura", Code: "wrf-taprm"},
    {Model: "WRF", Variable: "Humedad Relativa", Code: "wrf-hrprm"},
    {Model: "GFS", Variable: "Precipitación", Code: "gfs-pacum"},
    {Model: "GFS", Variable: "Temperatura", Code: "gfs-taprm"},
    {Model: "GFS", Variable: "Humedad Relativa", Code: "gfs-hrprm"}
  ];


  public goesProducts = [
    {Product: "Cloud and Moisture Imagery", Code:"GOES-ABI-L2-CMIPF-01", B:1, Band: 'Banda 1: 0.47 µm ("Blue")'},
    {Product: "Cloud and Moisture Imagery", Code:"GOES-ABI-L2-CMIPF-02", B:2, Band: 'Banda 2: 0.64 µm ("Red")'},
    {Product: "Cloud and Moisture Imagery", Code:"GOES-ABI-L2-CMIPF-03", B:3, Band: 'Banda 3: 0.86 µm ("Veggie")'},
    {Product: "Cloud and Moisture Imagery", Code:"GOES-ABI-L2-CMIPF-04", B:4, Band: 'Banda 4: 1.37 µm ("Cirrus")'},
    {Product: "Cloud and Moisture Imagery", Code:"GOES-ABI-L2-CMIPF-05", B:5, Band: 'Banda 5: 1.6 µm ("Snow/Ice")'},
    {Product: "Cloud and Moisture Imagery", Code:"GOES-ABI-L2-CMIPF-06", B:6, Band: 'Banda 6: 2.2 µm ("Cloud Particle Size")'},
    {Product: "Cloud and Moisture Imagery", Code:"GOES-ABI-L2-CMIPF-07", B:7, Band: 'Banda 7: 3.9 µm ("Shortwave Window")'},
    {Product: "Cloud and Moisture Imagery", Code:"GOES-ABI-L2-CMIPF-08", B:8, Band: 'Banda 8: 6.2 µm ("Upper-Level Tropospheric Water Vapor")'},
    {Product: "Cloud and Moisture Imagery", Code:"GOES-ABI-L2-CMIPF-09", B:9, Band: 'Banda 9: 6.9 µm ("Mid-Level Tropospheric Water Vapor")'},
    {Product: "Cloud and Moisture Imagery", Code:"GOES-ABI-L2-CMIPF-10", B:10, Band: 'Banda 10: 7.3 µm ("Lower-level Water Vapor")'},
    {Product: "Cloud and Moisture Imagery", Code:"GOES-ABI-L2-CMIPF-11", B:11, Band: 'Banda 11: 8.4 µm ("Cloud-Top Phase")'},
    {Product: "Cloud and Moisture Imagery", Code:"GOES-ABI-L2-CMIPF-12", B:12, Band: 'Banda 12: 9.6 µm ("Ozone")'},
    {Product: "Cloud and Moisture Imagery", Code:"GOES-ABI-L2-CMIPF-13", B:13, Band: 'Banda 13: 10.3 µm ("Clean" IR Longwave Window)'},
    {Product: "Cloud and Moisture Imagery", Code:"GOES-ABI-L2-CMIPF-14", B:14, Band: 'Banda 14: 11.2 µm ("IR" Longwave Window)'},
    {Product: "Cloud and Moisture Imagery", Code:"GOES-ABI-L2-CMIPF-15", B:15, Band: 'Banda 15: 12.3 µm ("Dirty" Longwave Window)'},
    {Product: "Cloud and Moisture Imagery", Code:"GOES-ABI-L2-CMIPF-16", B:16, Band: 'Banda 16: 13.3 µm ("CO2" Longwave Infrared)'}
  ]



}
