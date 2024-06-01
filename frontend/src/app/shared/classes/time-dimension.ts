import * as L from 'leaflet';

export class WMSLayerTimeControl {
  private map: L.Map;
  private layers: L.TileLayer.WMS[];
  private currentDateIndex: number;
  private timeInterval: number;
  private timeSerie: string[];
  private intervalId: any;
  private legendControl: L.Control;
  private legendDateElement: HTMLElement;
  private LControl: any;
  private product: string;
  private temporality: string;

  constructor(map: L.Map, LControl: any,layers: L.TileLayer.WMS[], timeInterval: number, timeSerie: string[], product: string, temporality: string) {
      this.map = map;
      this.layers = layers;
      this.timeInterval = timeInterval;
      this.currentDateIndex = 0;
      this.intervalId = null;
      this.timeSerie = timeSerie;
      this.LControl = LControl;
      this.product = product;
      this.temporality = temporality

      // Añadir la leyenda al mapa
      this.legendDateElement = document.createElement('div');
      this.legendDateElement.className = 'legend-date';
      this.legendControl = this.LControl({ position: 'bottomleft' });
      this.legendControl.onAdd = () => this.legendDateElement;
      this.legendControl.addTo(this.map);

      // Styles
      this.legendDateElement.style.backgroundColor = 'white';
      this.legendDateElement.style.color = 'black';
      this.legendDateElement.style.border = '1px solid #ccc';
      this.legendDateElement.style.padding = '5px';
      this.legendDateElement.style.fontSize = '16px';

      // Cargar todas las capas y solo dejar visible la primera
      if (this.layers.length > 0) {
          this.updateLegend();
          this.layers.forEach(layer => {layer.setOpacity(0).addTo(this.map);});
          this.layers[0].setOpacity(0.5);
      }
  }

  play() {
    if (this.intervalId == null) {
      this.intervalId = setInterval(() => {
          this.currentDateIndex++;
          if (this.currentDateIndex >= this.layers.length) {
              this.currentDateIndex = 0;
              this.layers.forEach(layer => {layer.setOpacity(0);});
          }
          this.updateLayerNext();
          this.updateLegend();
      }, this.timeInterval);
    }
  }

  stop() {
      if (this.intervalId !== null) {
          clearInterval(this.intervalId);
          this.intervalId = null;
      }
  }

  next(){
    this.currentDateIndex++;
    if (this.currentDateIndex >= this.layers.length) {
      this.currentDateIndex = 0;
      this.layers.forEach(layer => {layer.setOpacity(0);});
    }
    this.updateLayerNext();
    this.updateLegend();
  }

  previous(){
    this.currentDateIndex--;
    if (this.currentDateIndex < 0) {
      this.currentDateIndex = this.layers.length - 1;
      this.layers.forEach(layer => {layer.setOpacity(0);});
    }
    this.updateLayerPrevious();
    this.updateLegend();
  }

  destroy(){
    this.layers.forEach(layer => {layer.remove();});
    this.legendControl.remove();
  }

  private updateLayerNext() {
      this.layers[this.currentDateIndex - 1]?.setOpacity(0);
      this.layers[this.currentDateIndex]?.setOpacity(0.5);
  }

  private updateLayerPrevious() {
    this.layers[this.currentDateIndex + 1]?.setOpacity(0);
    this.layers[this.currentDateIndex]?.setOpacity(0.5);
  }

  private updateLegend() {
    const currentDate = this.timeSerie[this.currentDateIndex];
    if (currentDate) {
        // Add legend image
        const imageElement = document.createElement('img');
        imageElement.src = `assets/img/pacum-legend-${this.temporality}.webp`;
        imageElement.width = 600;
        // Add text legend
        this.legendDateElement.innerHTML = `${this.product.toUpperCase()}: ${currentDate} <br>`;
        this.legendDateElement.appendChild(imageElement);
    }
  }
}
