// TS MODULES AND LIBRARIES
import { CommonModule } from '@angular/common';
import { Component, ElementRef, Renderer2, ViewChild } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule, MatLabel } from '@angular/material/form-field';
import { MatSelect, MatOption } from '@angular/material/select';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { FormControl, FormsModule } from '@angular/forms';
import { ReactiveFormsModule } from '@angular/forms';
import { provideMomentDateAdapter } from '@angular/material-moment-adapter';

import {Observable} from 'rxjs';
import {map, startWith} from 'rxjs/operators';
import {AsyncPipe} from '@angular/common';
import {MatAutocompleteModule} from '@angular/material/autocomplete';

// JS LIBRARIES
import * as L from 'leaflet';
import * as PlotlyJS from 'plotly.js-dist-min';
import { PlotlyModule } from 'angular-plotly.js';
PlotlyModule.plotlyjs = PlotlyJS;

// CUSTOM COMPONENTS AND MODULES
import { AppTemplateComponent } from '../../shared/app-template/app-template.component';
import { DropdownComponent } from '../../shared/dropdown/dropdown.component';
import { LoadingComponent } from '../../shared/loading/loading.component';
import { environment } from '../../../environments/environment';
import { providers } from '../../modules/providers';
import { utils } from '../../modules/utils';
import { MatInputModule } from '@angular/material/input';
import { dataApp } from './hydropowers.component.config';




@Component({
  selector: 'app-hydropowers',
  standalone: true,
  providers: [provideMomentDateAdapter(new providers().dateFormat)],
  imports: [
    AppTemplateComponent,
    CommonModule,
    DropdownComponent,
    MatButtonModule,
    MatFormFieldModule,
    MatLabel,
    MatSelect,
    MatOption,
    MatDatepickerModule,
    FormsModule,
    ReactiveFormsModule,
    MatSlideToggleModule,
    LoadingComponent,
    PlotlyModule,
    MatInputModule,
    FormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatAutocompleteModule,
    ReactiveFormsModule,
    AsyncPipe
  ],
  templateUrl: './hydropowers.component.html',
  styleUrl: './hydropowers.component.css'
})


export class HydropowersComponent {

  // Components variables
  public isAuth: boolean = false;
  @ViewChild('template') template!: AppTemplateComponent;
  @ViewChild('panelPlot') panelPlot!: ElementRef;
  @ViewChild('table') table!: ElementRef;

  // Leaflet variables
  public map!: L.Map;
  public utilsApp = new utils();
  public draingeNetwork: any;

  // Time control Layers
  public isPlay:boolean = false;


  // Layers
  public isActiveHydropowers:boolean = true;
  public hydropowersLayer:any
  public isActiveCities:boolean = false;
  public citiesLayer:any
  public isActiveProvinces:boolean = false;
  public provincesLayer:any
  public isActiveCantons:boolean = false;
  public cantonsLayer:any


  // Basins
  public isActiveBasinAgoyan:boolean = false;
  public basinAgoyanLayer:any
  public isActiveBasinCoca:boolean = false;
  public basinCocaLayer:any
  public isActiveBasinDelsintanisagua:boolean = false;
  public basinDelsintanisaguaLayer:any
  public isActiveBasinDue:boolean = false;
  public basinDueLayer:any
  public isActiveBasinJubones:boolean = false;
  public basinJubonesLayer:any
  public isActiveBasinPaute:boolean = false;
  public basinPauteLayer:any


   // FFGS
   public isActiveASM:boolean = false;
   public isActiveFFG:boolean = false;
   public isActiveFMAP06:boolean = false;
   public isActiveFMAP24:boolean = false;
   public isActiveFFR12:boolean = false;
   public isActiveFFR24:boolean = false;
   public isActivePACUM24:boolean = false;
   public isActivePACUM48:boolean = false;
   public isActivePACUM72:boolean = false;
   public isActiveWarningPacum:boolean = false;
   public ffgsLayer:any;
   public ffgsLegend!:L.Control;
   public imgLegend!:L.Control;




  ngOnInit() {
    this.initializeMap();
  }


  public initializeMap(){
    // Add base map
    const osm = L.tileLayer(
      'https://abcd.basemaps.cartocdn.com/rastertiles/voyager_nolabels/{z}/{x}/{y}{r}.png', {
         zIndex: -1
      });
    this.map = L.map('map', { center: [-1.7, -78.5], zoom: 7, zoomControl: false });
    osm.addTo(this.map);

    // Resize map
    setTimeout(() => { this.map.invalidateSize() }, 10);

    // Add drainage network
    const urlDrainage = `${environment.urlGeoserver}/geoglows/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=geoglows:ecuador_drainage_network_geoglows&outputFormat=application/json`;
    fetch(urlDrainage)
    .then((response) => response.json())
    .then(data => {
      L.geoJSON(data, {style: {weight:0.7, color:"#4747C9"}}).addTo(this.map)
      this.draingeNetwork = L.geoJSON(data, {
          style: {weight: 12, color: "rgba(0, 0, 0, 0)"}
      }).addTo(this.map);
      //this.draingeNetwork.on("click", (e: L.LeafletMouseEvent) => this.getParamRiver(e));
    });


    this.citiesLayer = L.tileLayer(
      'https://tiles.stadiamaps.com/tiles/stamen_toner_labels/{z}/{x}/{y}{r}.png', {
        zIndex: 1100
      });

    this.provincesLayer = L.tileLayer.wms(`${environment.urlGeoserver}/ecuador-limits/wms?`, {
      layers: 'ecuador-limits:provincias',
      format: 'image/svg',
      transparent: true,
      version: '1.1.0',
      zIndex: 1000
    });

    this.cantonsLayer = L.tileLayer.wms(`${environment.urlGeoserver}/ecuador-limits/wms?`, {
      layers: 'ecuador-limits:cantones',
      format: 'image/svg',
      transparent: true,
      version: '1.1.0',
      zIndex: 900
    });


    // Add layers
    this.hydropowersLayer = L.tileLayer.wms(`${environment.urlGeoserver}/ecuador-limits/wms?`, {
      layers: 'ecuador-limits:hidroelectricas_mayores_50MW',
      format: 'image/svg',
      transparent: true,
      version: '1.1.0',
      zIndex: 1100,
    });
    this.hydropowersLayer.addTo(this.map);

    this.basinAgoyanLayer = L.tileLayer.wms(`${environment.urlGeoserver}/ecuador-limits/wms?`, {
      layers: 'ecuador-limits:agoyan',
      format: 'image/svg',
      transparent: true,
      version: '1.1.0',
      zIndex: 1100,
    });

    this.basinCocaLayer = L.tileLayer.wms(`${environment.urlGeoserver}/ecuador-limits/wms?`, {
      layers: 'ecuador-limits:coca',
      format: 'image/svg',
      transparent: true,
      version: '1.1.0',
      zIndex: 1100,
    });

    this.basinDelsintanisaguaLayer = L.tileLayer.wms(`${environment.urlGeoserver}/ecuador-limits/wms?`, {
      layers: 'ecuador-limits:delsintanisagua',
      format: 'image/svg',
      transparent: true,
      version: '1.1.0',
      zIndex: 1100,
    });

    this.basinDueLayer = L.tileLayer.wms(`${environment.urlGeoserver}/ecuador-limits/wms?`, {
      layers: 'ecuador-limits:due',
      format: 'image/svg',
      transparent: true,
      version: '1.1.0',
      zIndex: 1100,
    });

    this.basinJubonesLayer = L.tileLayer.wms(`${environment.urlGeoserver}/ecuador-limits/wms?`, {
      layers: 'ecuador-limits:jubones',
      format: 'image/svg',
      transparent: true,
      version: '1.1.0',
      zIndex: 1100,
    });

    this.basinPauteLayer = L.tileLayer.wms(`${environment.urlGeoserver}/ecuador-limits/wms?`, {
      layers: 'ecuador-limits:paute',
      format: 'image/svg',
      transparent: true,
      version: '1.1.0',
      zIndex: 1100,
    });
  }


  public updateOverlayers(isActiveLayer:boolean, layer:any){
    isActiveLayer ? layer.addTo(this.map) : this.map.removeLayer(layer);
  }

  public plotFFGS(workspace:string, param:string, title:string, type:string="ffgs", imgCond:boolean=true){
    param !== "asm" && (this.isActiveASM = false);
    param !== "ffg" && (this.isActiveFFG = false);
    param !== "fmap06" && (this.isActiveFMAP06 = false);
    param !== "fmap24" && (this.isActiveFMAP24 = false);
    param !== "ffr12" && (this.isActiveFFR12 = false);
    param !== "ffr24" && (this.isActiveFFR24 = false);
    param !== "daily_precipitation" && (this.isActivePACUM24 = false);
    param !== "2days_precipitation" && (this.isActivePACUM48 = false);
    param !== "3days_precipitation" && (this.isActivePACUM72 = false);
    param !== "advertencia_pacum" && (this.isActiveWarningPacum = false);

    this.ffgsLayer && this.map.removeLayer(this.ffgsLayer);
    this.ffgsLegend && this.ffgsLegend.remove();
    this.imgLegend && this.imgLegend.remove();

    const url = `${environment.urlGeoserver}/${workspace}/wms?`;

    if(this.isActiveASM || this.isActiveFFG || this.isActiveFMAP06 ||
       this.isActiveFMAP24 || this.isActiveFFR12 || this.isActiveFFR24 ||
       this.isActivePACUM24 || this.isActivePACUM48 || this.isActivePACUM72 ||
       this.isActiveWarningPacum){
          this.ffgsLayer = L.tileLayer.wms(url, {
            layers: `${workspace}:${param}`,
            format: 'image/png',
            transparent: true,
            version: '1.1.1',
            crs: L.CRS.EPSG4326
          }).addTo(this.map);

          let legendElement = document.createElement('div');

          this.ffgsLegend = new L.Control({ position: 'bottomleft' });
          this.ffgsLegend.onAdd = () => legendElement;
          this.ffgsLegend.addTo(this.map);

          legendElement.style.backgroundColor = 'rgba(255, 255, 255, 0.9)';
          legendElement.style.color = 'black';
          legendElement.style.padding = '5px';
          legendElement.style.borderRadius = "5px"

          const imageElement = document.createElement('img');
          imageElement.src = `assets/legend/${param}.png`;
          imageElement.style.maxWidth = "98%";
          imageElement.style.width = "400px";

          if(type==="ffgs"){
            let unit: string;
            const percentParams = ["asm", "fmap06", "fmap24"];
            unit = percentParams.includes(param) ? "(%)" : "(mm)";
            legendElement.innerHTML = `<b>${title} ${unit}</b><br><b>Última actualización:</b> ${this.utilsApp.getFFGSDate()}<br>`;
          }

          if(type==="pacum24"){
            legendElement.innerHTML = `<b>${title} en 24h (mm)</b><br>${this.utilsApp.getAcumulatedDate7()}<br>`;
          }

          if(type==="pacum48"){
            legendElement.innerHTML = `<b>${title} en 48h (mm)</b><br>${this.utilsApp.getAcumulatedDate48()}<br>`;
          }

          if(type==="pacum72"){
            legendElement.innerHTML = `<b>${title} en 72h (mm)</b><br>${this.utilsApp.getAcumulatedDate72()}<br>`;
          }

          if(type==="sat"){
            legendElement.innerHTML = `
            <b>${title}</b>
            <a href="https://inamhi.geoglows.org/hydrometeorological-charts/wp.jpg" target="_blank">Ver reporte</a>
            <div style="background-color:rgba(255,255,255,0.8); width:350px !important">
              <div style="padding-bottom:3px !important; padding-top: 3px !important;">
                <style>
                  .table-warning {
                    border-collapse: collapse;
                    width: 330px !important;
                    padding-bottom: 0px !important;
                    padding-top: 2px !important;
                  }

                  .th-warning, .td-warning {
                    padding: 2px;
                    text-align: center;
                    width: 25%;
                    font-weight: normal;
                    border: 1px solid black;
                  }
                  .bajo { background-color: #FFFFFF;}
                  .medio { background-color: #FFFF4D;}
                  .alto { background-color: #FFC44E;}
                  .muy-alto { background-color: #EF4C4D;}
                </style>
                <table class="table-warning" id="table-warning-selector">
                  <tr class="tr-warning">
                    <th class="th-warning bajo">Bajo</th>
                    <th class="th-warning medio">Medio</th>
                    <th class="th-warning alto">Alto</th>
                    <th class="th-warning muy-alto">Muy Alto</th>
                  </tr>
                </table>
              </div>
            </div>
            `;
          }

          if(imgCond){
            legendElement.appendChild(imageElement);
          }
    }
  }

}



// http://ec2-54-234-81-180.compute-1.amazonaws.com/geoserver/web/wicket/bookmarkable/org.geoserver.web.data.layer.NewLayerPage?5
