import { Component } from '@angular/core';
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
  }

  public resizeMap(): void {
    setTimeout(() => { this.map.invalidateSize() }, 10);
  }
}
