
export class dataApp{
  // Satellite based variables
  public satelliteVariables:string[] = ["Precipitación"];

  // Satellite based products
  public satelliteData =   [
    { Variable: 'Precipitación',  Product: 'PERSIANN CCS',     Code:"persiann-ccs-hourly",   Temporal: 'Horaria' },
    { Variable: 'Precipitación',  Product: 'PERSIANN CCS',     Code:"persiann-ccs-daily",    Temporal: 'Diaria' },
    { Variable: 'Precipitación',  Product: 'PERSIANN PDIR',    Code:"persiann-pdir-hourly",  Temporal: 'Horaria' },
    { Variable: 'Precipitación',  Product: 'PERSIANN PDIR',    Code:"persiann-pdir-daily",   Temporal: 'Diaria' },
    { Variable: 'Precipitación',  Product: 'IMERG Early Run',  Code:"imerg-early-hourly",    Temporal: 'Horaria' },
    { Variable: 'Precipitación',  Product: 'IMERG Early Run',  Code:"imerg-early-daily",     Temporal: 'Diaria' },
    { Variable: 'Precipitación',  Product: 'IMERG Late Run',   Code:"imerg-late-hourly",     Temporal: 'Horaria' },
    { Variable: 'Precipitación',  Product: 'IMERG Late Run',   Code:"imerg-late-daily",      Temporal: 'Diaria' },
  ];

  // GOES Products
  public goesProducts:string[] = ['Cloud and Moisture Imagery', 'Personalizado'];

  public goesData = [
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
  ];

  public forecastModels: string[] = ["WRF", "GFS", "ECMWF", "ICON"];

  public forecastData = [
    {Model: "WRF", Variable: "Precipitación",       Temporal: "Diaria",     Code: "wrf-precipitation"},
    {Model: "WRF", Variable: "Precipitación",       Temporal: "3 Horaria",  Code: "wrf-precipitation"},
    {Model: "WRF", Variable: "Temperatura",         Temporal: "Diaria",     Code: "wrf-temperature"},
    {Model: "WRF", Variable: "Temperatura",         Temporal: "3 Horaria",  Code: "wrf-temperature"},
    {Model: "WRF", Variable: "Humedad relativa",    Temporal: "Diaria",     Code: "wrf-humidity"},
    {Model: "WRF", Variable: "Humedad relativa",    Temporal: "3 Horaria",  Code: "wrf-humidity"},
    {Model: "WRF", Variable: "Velocidad del viento",Temporal: "Diaria",     Code: "wrf-windspeed"},
    {Model: "WRF", Variable: "Velocidad del viento",Temporal: "3 Horaria",  Code: "wrf-windspeed"}
  ]



}
