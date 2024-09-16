import * as L from 'leaflet';

export class WMSLayerTimeControl {
  private map: L.Map;
  public layers: L.TileLayer.WMS[];
  public currentDateIndex: number;
  private timeInterval: number;
  private intervalId: any;
  private dateControl: L.Control;
  private dateElement: HTMLElement;
  private LControl: any;
  private img: string;
  private imgCond: boolean;
  private reverse:boolean;
  private legendText:string[];

  constructor(
    map: L.Map,
    LControl: any,
    layers: L.TileLayer.WMS[],
    timeInterval: number,
    legendText: string[],
    img:string,
    imgCond:boolean = true,
    reverse:boolean = false) {

      this.map = map;
      this.layers = layers;
      this.timeInterval = timeInterval;
      this.currentDateIndex = reverse ? this.layers.length - 1 : 0;
      this.intervalId = null;
      this.LControl = LControl;
      this.img = img;
      this.legendText = legendText;
      this.imgCond = imgCond;
      this.reverse = reverse;

      this.dateElement = document.createElement('div');
      this.dateElement.className = 'legend-date';
      this.dateControl = this.LControl({ position: 'bottomleft' });
      this.dateControl.onAdd = () => this.dateElement;
      this.dateControl.addTo(this.map);
      this.dateElement.style.backgroundColor = 'rgba(255, 255, 255, 0.9)';
      this.dateElement.style.color = 'black';
      this.dateElement.style.padding = '5px';
      this.dateElement.style.fontSize = '0.8rem';
      this.dateElement.style.borderRadius = "5px"


      // Cargar todas las capas y solo dejar visible la primera
      if (this.layers.length > 0) {
          this.updateLegend();

          if(this.reverse){
            for (let i = this.layers.length - 1; i >= 0; i--) {
              this.layers[i].setOpacity(0).addTo(this.map);
            }
          }else{
            this.layers.forEach(layer => {layer.setOpacity(0).addTo(this.map);});
          }

          this.layers[this.currentDateIndex].setOpacity(0.9);
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
    this.dateControl.remove();
  }

  setStart(){
    this.currentDateIndex = 0;
    this.layers.map((layer) => { layer.setOpacity(0)});
    this.layers[this.currentDateIndex]?.setOpacity(0.9);
    this.updateLegend();
  }

  getCurrentIndexS(){
    return this.currentDateIndex;
  }

  private updateLayerNext() {
      this.layers[this.currentDateIndex - 1]?.setOpacity(0);
      this.layers[this.currentDateIndex]?.setOpacity(0.9);
  }

  private updateLayerPrevious() {
    this.layers[this.currentDateIndex + 1]?.setOpacity(0);
    this.layers[this.currentDateIndex]?.setOpacity(0.9);
  }

  private updateLegend() {
    const currentLegend = this.legendText[this.currentDateIndex];
    if (currentLegend) {
      this.dateElement.innerHTML = `${currentLegend} <br>`;
      if(this.imgCond){
        const imageElement = document.createElement('img');
        imageElement.src = this.img;
        imageElement.style.paddingTop = "4px";
        imageElement.style.width = "400px";
        imageElement.style.maxWidth = "98%";
        this.dateElement.appendChild(imageElement);
      }
    }
  }
}

