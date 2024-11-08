import { Component } from '@angular/core';
import { environment } from '../../../environments/environment';
import * as L from 'leaflet';

@Component({
  selector: 'app-map',
  standalone: true,
  imports: [],
  templateUrl: './map.component.html',
  styleUrl: './map.component.css'
})
export class MapComponent {

  // Map Variable
  public map!: L.Map;

  // Overlays
  public isActiveNationalLayer: boolean = true;
  public nationalLayer: any;
  public isActiveProvinceLayer: boolean = true;
  public provinceLayer: any;



  ngOnInit(){
    // Initialized basemap layer
    const osm = L.tileLayer(
      'https://abcd.basemaps.cartocdn.com/rastertiles/voyager_nolabels/{z}/{x}/{y}{r}.png', {
         zIndex: -1
      });
    this.map = L.map('map', { center: [-1.7, -78.5], zoom: 7, zoomControl: false });
    osm.addTo(this.map);

    // Add INAMHI Logo
    L.control.zoom({ position: 'topright' }).addTo(this.map);
    const logoControl = new L.Control({ position: 'topleft' });
    logoControl.onAdd = () => {
      const image = document.createElement('img');
      image.className = "inamhi-logo";
      image.src = 'assets/img/inamhi-white-logo.png';
      return(image)
    }
    logoControl.addTo(this.map);

    // Resize the map
    this.resizeMap();

    //
    this.nationalLayer = L.tileLayer.wms(`http://ec2-54-234-81-180.compute-1.amazonaws.com/geoserver/ecuador/wms?`, {
      layers: 'ecuador:nacional',
      format: 'image/svg',
      transparent: true,
      version: '1.1.0',
      zIndex: 1000
    });
    this.nationalLayer.addTo(this.map);

    this.provinceLayer = L.tileLayer.wms(`http://ec2-54-234-81-180.compute-1.amazonaws.com/geoserver/ecuador/wms?`, {
      layers: 'ecuador:provincial',
      format: 'image/svg',
      transparent: true,
      version: '1.1.0',
      zIndex: 1000
    });
    this.provinceLayer.addTo(this.map);

    //${environment.urlGeoserver}
  }

  public resizeMap(): void {
    setTimeout(() => { this.map.invalidateSize() }, 10);
  }
}
