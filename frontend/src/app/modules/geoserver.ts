import * as L from 'leaflet';

export class Geoserver{
  public async getLastLayers(wmsUrl: string, lastLayerNumber: number): Promise<string[]> {
    try {
        const response = await fetch(wmsUrl);
        const text = await response.text();
        const parser = new DOMParser();
        const xmlDoc = parser.parseFromString(text, "application/xml");
        const layers = xmlDoc.getElementsByTagName("Layer");
        const layerList: string[] = [];
        for (let i = 0; i < layers.length; i++) {
            const layerNameElement = layers[i].getElementsByTagName("Name")[0];
            if (layerNameElement && layerNameElement.textContent) {
                layerList.push(layerNameElement.textContent);
            }
        }
        return layerList.slice(-lastLayerNumber);
    } catch (error) {
        console.error('Error al solicitar GetCapabilities:', error);
        return [];
    }
  }

  public getWMSLayer(url: string, layer: string): any {
    let leafletLayer = L.tileLayer.wms(url, {
      layers: layer,
      format: 'image/png',
      transparent: true,
      version: '1.1.1',
      crs: L.CRS.EPSG4326,
    });
    return leafletLayer;
  }
}
