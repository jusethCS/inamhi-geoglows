declare module 'leaflet-image' {
  import * as L from 'leaflet';
  function leafletImage(map: L.Map, callback: (err: any, canvas: HTMLCanvasElement) => void): void;
  export = leafletImage;
}
