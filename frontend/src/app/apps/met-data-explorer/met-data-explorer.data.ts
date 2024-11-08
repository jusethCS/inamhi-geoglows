export class dataApp{
  // GOES Products
  public goesProducts:string[] = ['Cloud and Moisture Imagery', 'Custom RGB Products'];
  public goesOverlay:string[] = ['None', 'Group Energy Density'];

  public goesData = [
    {Product: "Cloud and Moisture Imagery", Code:"goes_abi_l2_cmipf_13", B:13, Band: 'Banda 13: 10.3 µm ("Clean" IR Longwave Window)', Tag: "(°C)"},

    {Product: "Group Energy Density", Code:"goes_glm_l2_lcfa", B:1, Band: 'Group Energy Density', Tag: ""},
  ];


}
