import * as L from 'leaflet';

export class WMSLayerTimeControl {
  private map: L.Map;
  private layers: L.TileLayer.WMS[];
  private currentDateIndex: number;
  private timeInterval: number;
  private timeSerie: string[];
  private intervalId: any;
  private dateControl: L.Control;
  private dateElement: HTMLElement;
  private legendControl: L.Control;
  private legendElement: HTMLElement;
  private LControl: any;
  private product: string;
  private img: string;

  constructor(
    map: L.Map, LControl: any,layers: L.TileLayer.WMS[],
    timeInterval: number, timeSerie: string[], product: string,
    img:string ) {

      this.map = map;
      this.layers = layers;
      this.timeInterval = timeInterval;
      this.currentDateIndex = 0;
      this.intervalId = null;
      this.timeSerie = timeSerie;
      this.LControl = LControl;
      this.product = product;
      this.img = img;

      // Añadir la fecha al mapa
      this.dateElement = document.createElement('div');
      this.dateElement.className = 'legend-date';
      this.dateControl = this.LControl({ position: 'bottomleft' });
      this.dateControl.onAdd = () => this.dateElement;
      this.dateControl.addTo(this.map);
      this.dateElement.style.backgroundColor = 'rgba(255, 255, 255, 0.9)';
      this.dateElement.style.color = 'black';
      this.dateElement.style.fontWeight = "bold";
      this.dateElement.style.padding = '5px';
      this.dateElement.style.fontSize = '0.8rem';
      this.dateElement.style.borderRadius = "5px"

      // Añadir la leyenda al mapa
      this.legendElement = document.createElement('div');
      this.legendControl = this.LControl({ position: 'bottomleft' });
      this.legendControl.onAdd = () => this.legendElement;
      this.legendControl.addTo(this.map);
      this.legendElement.style.backgroundColor = 'rgba(255, 255, 255, 0.9)';
      this.legendElement.style.color = 'black';
      this.legendElement.style.padding = '5px';
      this.legendElement.style.borderRadius = "5px"


      // Cargar todas las capas y solo dejar visible la primera
      if (this.layers.length > 0) {
          this.updateLegend();
          this.layers.forEach(layer => {layer.setOpacity(0).addTo(this.map);});
          this.layers[0].setOpacity(0.6);
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
    this.dateControl.remove();
  }

  private updateLayerNext() {
      this.layers[this.currentDateIndex - 1]?.setOpacity(0);
      this.layers[this.currentDateIndex]?.setOpacity(0.6);
  }

  private updateLayerPrevious() {
    this.layers[this.currentDateIndex + 1]?.setOpacity(0);
    this.layers[this.currentDateIndex]?.setOpacity(0.6);
  }

  private updateLegend() {
    const currentDate = this.timeSerie[this.currentDateIndex];
    if (currentDate) {
        // Add legend image
        const imageElement = document.createElement('img');
        imageElement.src = this.img;
        imageElement.height = 300;
        this.legendElement.innerHTML = "";
        this.legendElement.appendChild(imageElement);
        // Add text legend
        this.dateElement.innerHTML = `${this.product.toUpperCase()}: ${currentDate} <br>`;

    }
  }
}
