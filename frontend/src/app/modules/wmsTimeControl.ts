import * as L from 'leaflet';

export class WMSTimeControl {
  private map: L.Map;
  public layers: L.TileLayer.WMS[];
  public overlays: L.TileLayer.WMS[] | undefined;
  public currentDateIndex: number;
  private dateControl: L.Control;
  private dateElement: HTMLElement;
  private interval: any;
  private reverse:boolean;
  private titles:string[];
  private img: string | undefined;


  constructor(
    map: L.Map,
    layers: L.TileLayer.WMS[],
    overlays: L.TileLayer.WMS[] | undefined,
    img: string | undefined,
    titles:string[],
    reverse:boolean = false
  ) {

    this.map = map;
    this.layers = layers;
    this.overlays = overlays;
    this.currentDateIndex = reverse ? this.layers.length - 1 : 0;
    this.interval = null;
    this.img = img;
    this.titles=titles;
    this.reverse = reverse;

    // Create date element and control
    this.dateElement = document.createElement('div');
    this.dateElement.className = 'legend-date';
    this.dateControl = new L.Control({ position: 'bottomleft' });
    this.dateControl.onAdd = () => this.dateElement;
    this.dateControl.addTo(this.map);
    this.dateElement.style.backgroundColor = 'rgba(255, 255, 255, 0.9)';
    this.dateElement.style.color = 'black';
    this.dateElement.style.padding = '5px';
    this.dateElement.style.fontSize = '0.8rem';
    this.dateElement.style.borderRadius = "5px"

    // Cargar todas las capas y solo dejar visible la primera
    if (this.layers.length > 0) {
      const startIndex = this.reverse ? this.layers.length - 1 : 0;
      const endIndex = this.reverse ? -1 : this.layers.length;
      const step = this.reverse ? -1 : 1;

      // Cargar layers y overlays al mismo tiempo
      for (let i = startIndex; i !== endIndex; i += step) {
        this.layers[i].setOpacity(0).addTo(this.map);
        if (this.overlays && this.overlays.length > 0) {
          this.overlays[i].setOpacity(0).addTo(this.map);
        }
      }

      // Establecer la opacidad de las capas visibles
      this.layers[this.currentDateIndex].setOpacity(1);
      if (this.overlays && this.overlays.length > 0) {
        this.overlays[this.currentDateIndex].setOpacity(1);
      }

      this.updateLegend();
    }

  }


  public setStart(){
    this.currentDateIndex = 0;
    this.layers.map((layer) => { layer.setOpacity(0)});
    this.layers[this.currentDateIndex]?.setOpacity(1);
    if (this.overlays && this.overlays.length > 0) {
      this.overlays.map((layer) => { layer.setOpacity(0)});
      this.overlays[this.currentDateIndex]?.setOpacity(1);
    }
    this.updateLegend();
  }

  private updateNextLayer(){
    this.layers[this.currentDateIndex - 1]?.setOpacity(0);
    this.layers[this.currentDateIndex]?.setOpacity(1);
    if (this.overlays && this.overlays.length > 0) {
      this.overlays[this.currentDateIndex - 1]?.setOpacity(0);
      this.overlays[this.currentDateIndex]?.setOpacity(1);
    }
    this.updateLegend();
  }

  public next(){
    this.currentDateIndex++;
    if (this.currentDateIndex >= this.layers.length) {
      this.currentDateIndex = 0;
      this.layers.forEach(layer => {layer.setOpacity(0)});
      if (this.overlays && this.overlays.length > 0) {
        this.overlays.forEach(layer => {layer.setOpacity(0)});
      }
    }
    this.updateNextLayer();
  }

  private updatePreviousLayer(){
    this.layers[this.currentDateIndex + 1]?.setOpacity(0);
    this.layers[this.currentDateIndex]?.setOpacity(1);
    if (this.overlays && this.overlays.length > 0) {
      this.overlays[this.currentDateIndex + 1]?.setOpacity(0);
      this.overlays[this.currentDateIndex]?.setOpacity(1);
    }
    this.updateLegend();
  }

  public previous(){
    this.currentDateIndex--;
    if (this.currentDateIndex < 0) {
      this.currentDateIndex = this.layers.length - 1;
      this.layers.forEach(layer => {layer.setOpacity(0)});
      if (this.overlays && this.overlays.length > 0) {
        this.overlays.forEach(layer => {layer.setOpacity(0)});
      }
    }
    this.updatePreviousLayer();
  }

  public play(){
    if (this.interval == null){
      this.interval = setInterval(() => {
        this.next()
      }, 300);
    }
  }

  public pause(){
    if (this.interval !== null) {
      clearInterval(this.interval);
      this.interval = null;
    }
  }

  public destroy(){
    this.pause();
    this.layers.forEach(layer => {layer.remove()});
    if (this.overlays && this.overlays.length > 0){
      this.overlays.forEach(layer => {layer.remove()});
    }
    this.dateControl.remove();
  }


  private updateLegend(){
    const currentTitle = this.titles[this.currentDateIndex];
    if (currentTitle){
      this.dateElement.innerHTML = `${currentTitle} <br>`
    }
    if(this.img){
      const imageElement = document.createElement('img');
      imageElement.src = this.img;
      imageElement.style.paddingTop = "4px";
      imageElement.style.width = "350px";
      imageElement.style.maxWidth = "98%";
      this.dateElement.appendChild(imageElement);
    }
  }

}
