export class dataApp{
  // GOES Products
  public goesProducts:string[] = ['Cloud and Moisture Imagery', 'Custom RGB Products'];
  public goesOverlay:string[] = ['None', 'Group Energy Density'];

  public goesData = [
    {Product: "Cloud and Moisture Imagery", Code:"GOES-ABI-L2-CMIPF-01", B:1, Band: 'Banda 1: 0.47 µm ("Blue")', Tag: ""},
    {Product: "Cloud and Moisture Imagery", Code:"GOES-ABI-L2-CMIPF-02", B:2, Band: 'Banda 2: 0.64 µm ("Red")', Tag: ""},
    {Product: "Cloud and Moisture Imagery", Code:"GOES-ABI-L2-CMIPF-03", B:3, Band: 'Banda 3: 0.86 µm ("Veggie")', Tag: ""},
    {Product: "Cloud and Moisture Imagery", Code:"GOES-ABI-L2-CMIPF-04", B:4, Band: 'Banda 4: 1.37 µm ("Cirrus")', Tag: ""},
    {Product: "Cloud and Moisture Imagery", Code:"GOES-ABI-L2-CMIPF-05", B:5, Band: 'Banda 5: 1.6 µm ("Snow/Ice")', Tag: ""},
    {Product: "Cloud and Moisture Imagery", Code:"GOES-ABI-L2-CMIPF-06", B:6, Band: 'Banda 6: 2.2 µm ("Cloud Particle Size")', Tag: ""},
    {Product: "Cloud and Moisture Imagery", Code:"GOES-ABI-L2-CMIPF-07", B:7, Band: 'Banda 7: 3.9 µm ("Shortwave Window")', Tag: "(°C)"},
    {Product: "Cloud and Moisture Imagery", Code:"GOES-ABI-L2-CMIPF-08", B:8, Band: 'Banda 8: 6.2 µm ("Upper-Level Tropospheric Water Vapor")', Tag: "(°C)"},
    {Product: "Cloud and Moisture Imagery", Code:"GOES-ABI-L2-CMIPF-09", B:9, Band: 'Banda 9: 6.9 µm ("Mid-Level Tropospheric Water Vapor")', Tag: "(°C)"},
    {Product: "Cloud and Moisture Imagery", Code:"GOES-ABI-L2-CMIPF-10", B:10, Band: 'Banda 10: 7.3 µm ("Lower-level Water Vapor")', Tag: "(°C)"},
    {Product: "Cloud and Moisture Imagery", Code:"GOES-ABI-L2-CMIPF-11", B:11, Band: 'Banda 11: 8.4 µm ("Cloud-Top Phase")', Tag: "(°C)"},
    {Product: "Cloud and Moisture Imagery", Code:"GOES-ABI-L2-CMIPF-12", B:12, Band: 'Banda 12: 9.6 µm ("Ozone")', Tag: "(°C)"},
    {Product: "Cloud and Moisture Imagery", Code:"GOES-ABI-L2-CMIPF-13", B:13, Band: 'Banda 13: 10.3 µm ("Clean" IR Longwave Window)', Tag: "(°C)"},
    {Product: "Cloud and Moisture Imagery", Code:"GOES-ABI-L2-CMIPF-14", B:14, Band: 'Banda 14: 11.2 µm ("IR" Longwave Window)', Tag: "(°C)"},
    {Product: "Cloud and Moisture Imagery", Code:"GOES-ABI-L2-CMIPF-15", B:15, Band: 'Banda 15: 12.3 µm ("Dirty" Longwave Window)', Tag: "(°C)"},
    {Product: "Cloud and Moisture Imagery", Code:"GOES-ABI-L2-CMIPF-16", B:16, Band: 'Banda 16: 13.3 µm ("CO2" Longwave Infrared)', Tag: "(°C)"},

    {Product: "Custom RGB Products", Code:"GOES-RGB-TRUE-COLOR",       B:16, Band: 'True Color', Tag: ""},
    {Product: "Custom RGB Products", Code:"GOES-RGB-DAY-CLOUD-PHASE",  B:16, Band: 'Day Cloud Phase Distinction', Tag: ""},
    {Product: "Custom RGB Products", Code:"GOES-RGB-FIRE-TEMPERATURE", B:16, Band: 'Fire Temperature', Tag: ""},

    {Product: "Group Energy Density", Code:"GOES-ABI-L2-CMIPF-13", B:1, Band: 'Group Energy Density', Tag: ""},
  ];


}
