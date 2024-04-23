import { Component } from '@angular/core';
import { AppHeaderComponent } from '../../shared/components/app-header/app-header.component';
import { CommonModule } from '@angular/common';


@Component({
  selector: 'app-climate-trends',
  standalone: true,
  templateUrl: './climate-trends.component.html',
  styleUrl: './climate-trends.component.css',
  imports: [AppHeaderComponent, CommonModule]
})


export class ClimateTrendsComponent {

  // -------------------------------------------------------------------- //
  //                           CLASS ATTRIBUTES                           //
  // -------------------------------------------------------------------- //

  // Leaflet variables
  L: any;
  map: any;

  // State variable for panel activation
  panelActive: boolean = true;



  // -------------------------------------------------------------------- //
  //                          CLASS CONSTRUCTOR                           //
  // -------------------------------------------------------------------- //
  constructor() { }

  async ngOnInit() {
    // Dinamically import Leaflet
    this.L = await import('leaflet');

    // Initialize the map
    this.map = this.L.map("map");
    this.map.setView([-1.7, -78.5], 7)
    this.L.tileLayer(
      'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
    ).addTo(this.map);

    var wmsLayer = this.L.tileLayer.wms(
      'http://ec2-3-211-227-44.compute-1.amazonaws.com/geoserver/chirps/wms', {
        layers: 'chirps:2024-01-01',
        format: 'image/png',
        transparent: true,
        version: "1.1.1",
      }).addTo(this.map);
  }

  // -------------------------------------------------------------------- //
  //                            CLASS METHODS                             //
  // -------------------------------------------------------------------- //

  // Open or close panel
  isPanelActive(panelActivateEvent: boolean){
    this.panelActive = panelActivateEvent;
    setTimeout(() => {this.map.invalidateSize()}, 10);
  }


}
