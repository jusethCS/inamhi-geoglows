import * as L from 'leaflet';

export class Geoserver{


  public async getAvailableDatesFromImageMosaic(url: string, layer: string): Promise<string[]> {
    const getCapabilitiesUrl = `${url}?service=WMS&version=1.1.1&request=GetCapabilities`;

    try {
        // Fetch XML data from the WMS service
        const response = await fetch(getCapabilitiesUrl);
        const xmlText = await response.text();

        // Parse XML response
        const parser = new DOMParser();
        const xmlDoc = parser.parseFromString(xmlText, "application/xml");

        // Use querySelector to directly access the specific layer element by name
        const layerElement = Array.from(xmlDoc.querySelectorAll("Layer"))
            .find(layerNode => layerNode.querySelector("Name")?.textContent === layer);

        if (!layerElement) return []; // Return empty if layer is not found

        // Directly access the time extent within the layer
        const timeExtent = layerElement.querySelector("Extent[name='time']");
        if (!timeExtent || !timeExtent.textContent) return []; // Return empty if no time extent is found

        // Split and slice the time values to get the latest dates
        const dates = timeExtent.textContent.split(",");
        return dates.slice(-10);  // Return only the last 10 dates for efficiency

    } catch (error) {
        console.error("Error fetching dates:", error);
        return [];
    }
  }



  public getWMSFromImageMosaic(url: string, layer: string, time: string): any {
    const options = {
      layers: layer,
      format: 'image/png',
      transparent: true,
      version: '1.1.1',
      crs: L.CRS.EPSG4326,
      time: time
    } as L.WMSOptions & { time: string };
    return L.tileLayer.wms(url, options);
  }






}
