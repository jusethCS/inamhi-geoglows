// TS MODULES AND LIBRARIES
import { CommonModule } from '@angular/common';
import { Component, ViewChild } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule, MatLabel } from '@angular/material/form-field';
import { MatSelect, MatOption } from '@angular/material/select';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { FormGroup, FormControl, FormsModule } from '@angular/forms';
import { ReactiveFormsModule, FormBuilder } from '@angular/forms';
import { provideMomentDateAdapter } from '@angular/material-moment-adapter';

// JS LIBRARIES
import * as L from 'leaflet';
import * as PlotlyJS from 'plotly.js-dist-min';
import { PlotlyModule } from 'angular-plotly.js';
PlotlyModule.plotlyjs = PlotlyJS;

// CUSTOM COMPONENTS AND MODULES
import { WMSLayerTimeControl } from '../../modules/timeDimension';
import { AppTemplateComponent } from '../../shared/app-template/app-template.component';
import { DropdownComponent } from '../../shared/dropdown/dropdown.component';
import { LoadingComponent } from '../../shared/loading/loading.component';
import { environment } from '../../../environments/environment';
import { providers } from '../../modules/providers';
import { utils } from '../../modules/utils';
import { plotTemplates } from "../../modules/plotTemplates";
import { dataApp } from './climate-trends.component.config';


@Component({
  selector: 'app-climate-trends',
  standalone: true,
  templateUrl: './climate-trends.component.html',
  styleUrl: './climate-trends.component.css',
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
  ],
})

export class ClimateTrendsComponent {  // Components variables
  public isAuth: boolean = false;
  @ViewChild('template') template!: AppTemplateComponent;

  // Leaflet variables
  public map!: L.Map;
  public dataAppConfig = new dataApp();
  public utilsApp = new utils();
  public plotTemplate = new plotTemplates();

  // Satellite based product
  public satelliteData = this.dataAppConfig.satelliteData;
  public satelliteVariable: string[] = this.dataAppConfig.satelliteVariables;
  public selectedSatelliteVariable: string = this.satelliteVariable[0];
  public satelliteProducts: any = [];
  public selectedSatelliteProduct: string = "";
  public satelliteTemporal: any = [];
  public selectedSatelliteTemporal: string = "";
  public satelliteDateRange: FormGroup = new FormGroup({
    start: new FormControl<Date | null>(null),
    end: new FormControl<Date | null>(null),
  });
  public satelliteMinDate: Date = new Date(2004, 0, 1); //2004-01-01
  public satelliteMaxDate: Date = new Date();

  // Layer information and plot
  public timeControl: WMSLayerTimeControl | undefined;
  public isActiveInfoLayers:boolean = false;
  public isPointPlotClass:boolean = false;
  public activeURLLayer: string = '';
  public activeLayers: string[] = [];
  public activeLayersCode:string[] = [];
  public activeDates: string[] = [];
  public isReadyData: boolean = false;
  public plotClass: string = "satellite";
  public goesBTemp:boolean = false;

  // Plot templates
  public precPlot: any = {};
  public tempPlot: any = {};
  public humPlot: any = {};
  public windPlot: any = {};

  // Base layers
  public citiesLayer: any;
  public provinceLayer: any;
  public cantonLayer:any;
  public isActiveCitiesLayer:boolean = true;
  public isActiveProvinceLayer: boolean = true;
  public isActiveCantonLayer:boolean = false;

  // Point plot
  public latC: any;
  public lonC: any;

  // Time control Layers
  public isPlay:boolean = false;


  // Plot - geographical area
  public ecuadorData = this.dataAppConfig.ecuador;
  public provinces = this.dataAppConfig.provinces;
  public selectedProvince = this.provinces[0];
  public cantons: string[] = [];
  public selectedCanton: string = "";
  public geojsonLayer!: L.GeoJSON;
  public selectedCode:string = "";

  constructor(private formBuilder: FormBuilder){}

  ngOnInit() {
    this.initializeMap();
    this.initializeOverlays();
    this.resizeMap();
    this.updateSatelliteProduct();
    this.updateSatelliteTemporal();
    this.initFormDate();
    this.updateCanton();
  }



  public initializeMap() {
    // Base maps
    const osm = L.tileLayer(
      'https://abcd.basemaps.cartocdn.com/rastertiles/voyager_nolabels/{z}/{x}/{y}{r}.png', {
         zIndex: -1
      });
    const carto = L.tileLayer(
      'https://abcd.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}{r}.png', {
        zIndex: -1
      });
    const baseMaps = {
      "Mapa claro": osm,
      'Mapa oscuro': carto
    };

    // Add base map
    this.map = L.map('map', { center: [-1.7, -78.5], zoom: 7, zoomControl: false });
    osm.addTo(this.map);

    // Add controls
    L.control.layers(baseMaps, {}, { position: 'topright' }).addTo(this.map);
    L.control.zoom({ position: 'topright' }).addTo(this.map);

    // Add logo control
    const logoControl = new L.Control({ position: 'topleft' });
    logoControl.onAdd = () => {
      const image = document.createElement('img');
      image.className = "inamhi-logo";
      image.src = 'assets/img/inamhi-white-logo.png';
      return(image)
    }
    logoControl.addTo(this.map);

    // Add pixel info control
    const infoControl = new L.Control({ position: 'topright' });
    infoControl.onAdd = () => {
      const infoDiv = document.createElement('div');
      infoDiv.className = "d-flex justify-content-center align-items-center info-control"
      infoDiv.innerHTML = "<i class='fa-regular fa-circle-info'></i>"
      L.DomEvent.on(infoDiv, 'click', L.DomEvent.stopPropagation);
      L.DomEvent.on(infoDiv, 'click', L.DomEvent.preventDefault);
      infoDiv.addEventListener('click', () => {
        setTimeout(() => {
          this.isActiveInfoLayers = !this.isActiveInfoLayers;
          if (this.isActiveInfoLayers) {
            infoDiv.style.backgroundColor = '#ADADAD';
            this.isPointPlotClass = true;
          } else {
            infoDiv.style.backgroundColor = 'white';
            this.isPointPlotClass = false;
          };
        }, 10);
      });
      return(infoDiv)
    }
    infoControl.addTo(this.map);

    // Add Point plot info
    this.map.on('click', async (evt: L.LeafletMouseEvent) => {
      this.getPointInfo(evt);
    });
  }

  public initializeOverlays(){
    this.citiesLayer = L.tileLayer(
      'https://tiles.stadiamaps.com/tiles/stamen_toner_labels/{z}/{x}/{y}{r}.png', {
        zIndex: 1100
      });
    this.citiesLayer.addTo(this.map);
    this.provinceLayer = L.tileLayer.wms(`${environment.urlGeoserver}/ecuador-limits/wms?`, {
      layers: 'ecuador-limits:provincias',
      format: 'image/png',
      transparent: true,
      version: '1.1.0',
      zIndex: 1000
    });
    this.provinceLayer.addTo(this.map);
    this.cantonLayer = L.tileLayer.wms(`${environment.urlGeoserver}/ecuador-limits/wms?`, {
      layers: 'ecuador-limits:cantones',
      format: 'image/png',
      transparent: true,
      version: '1.1.0',
      zIndex: 900
    });
    const overlayers = [this.cantonLayer, this.provinceLayer, this.citiesLayer];
    this.map.on('layeradd', function(){
      overlayers.map(layer => layer.bringToFront());
    });
  }


  public resizeMap(): void {
    setTimeout(() => { this.map.invalidateSize() }, 10);
  }

  public getLeafletLayer(url: string, layer: string): any {
    let leafletLayer = L.tileLayer.wms(url, {
      layers: layer,
      format: 'image/png',
      transparent: true,
      version: '1.1.1',
      crs: L.CRS.EPSG4326,
    });
    leafletLayer.setZIndex(10);
    return leafletLayer;
  }

  async getFeatureInfo(evt: L.LeafletMouseEvent, baseUrl: string, layer: string) {
    const point = this.map!.latLngToContainerPoint(evt.latlng);
    const size = this.map!.getSize();
    const bounds = this.map!.getBounds();
    const sw = bounds.getSouthWest();
    const ne = bounds.getNorthEast();
    const params = {
      request: 'GetFeatureInfo',
      service: 'WMS',
      srs: 'EPSG:4326',
      styles: '',
      transparent: true,
      version: '1.1.1',
      format: 'application/json',
      bbox: `${sw.lng},${sw.lat},${ne.lng},${ne.lat}`,
      height: size.y.toString(),
      width: size.x.toString(),
      layers: layer,
      query_layers: layer,
      info_format: 'application/json',
      x: point.x.toString(),
      y: point.y.toString(),
    };
    const url = this.utilsApp.buildUrl(baseUrl, params);
    let data: any;
    try{
      const response = await fetch(url);
      data = await response.json();
    }catch(error){
      if (error instanceof Error) {
        console.error('Error capturado:', error.message);
      } else {
        console.error('Error inesperado:', error);
      }
      return undefined;
    }
    if (data.features && data.features.length > 0 && data.features[0].properties) {
      const grayIndexString = data.features[0].properties.GRAY_INDEX;
      return(grayIndexString);
    }
    return undefined;
  }




  public updateSatelliteProduct(): void {
    const filtered = new Set<string>();
    this.satelliteData.forEach(item => {
      if (item.Variable === this.selectedSatelliteVariable) {
        filtered.add(item.Product)}});
    this.satelliteProducts = Array.from(filtered);
    this.selectedSatelliteProduct = this.satelliteProducts[0] || null;
  }

  public updateSatelliteTemporal(): void {
    const filtered = new Set<string>();
    this.satelliteData.forEach(item => {
      if (item.Variable === this.selectedSatelliteVariable && item.Product === this.selectedSatelliteProduct) {
        filtered.add(item.Temporal)}});
    this.satelliteTemporal = Array.from(filtered);
    this.selectedSatelliteTemporal = this.satelliteTemporal[0] || null;
  }

  public initFormDate(): void {
    const startDate = new Date();
    startDate.setDate(this.satelliteMaxDate.getDate() - 2)
    const endDate = new Date();
    endDate.setDate(this.satelliteMaxDate.getDate() - 1)
    this.satelliteDateRange = this.formBuilder.group({ start: [startDate], end: [endDate]});
  }

  public updateSatelliteLayer(): void {
    this.isPlay = false;
    let layerCode = this.satelliteData.filter(
        (item) =>
          item.Variable === this.selectedSatelliteVariable &&
          item.Product === this.selectedSatelliteProduct &&
          item.Temporal === this.selectedSatelliteTemporal
      )[0].Code;
    let startDate = this.satelliteDateRange.value.start;
    let endDate = this.satelliteDateRange.value.end;
    let url = `${environment.urlGeoserver}/${layerCode}/wms`;
    let layers = this.utilsApp
                  .generateSatelliteDates(startDate, endDate, this.selectedSatelliteTemporal, true)
                  .map((date) => this.getLeafletLayer(url, `${layerCode}:${date}`))
    let dates = this.utilsApp
                  .generateSatelliteDates(startDate, endDate, this.selectedSatelliteTemporal, false)
    let layerName = `${this.selectedSatelliteProduct} ${this.selectedSatelliteTemporal}`;
    let legendSRC = `assets/img/legend-${layerCode}.png`
    if (this.timeControl !== undefined) {
      this.timeControl.destroy();
    }
    this.timeControl = new WMSLayerTimeControl(this.map, L.control, layers, 500, dates, layerName, legendSRC);

    // Status plot
    this.activeURLLayer = url;
    this.activeLayers = layers.map(layer => layer.options.layers);
    this.activeLayersCode = layers.map(layer => layer.options.layers);
    this.activeDates = dates;
    this.plotClass = "satellite";
  }



  public playTimeControl(){
    if (this.isPlay) {
      this.isPlay = false;
      this.timeControl?.stop();
    } else {
      this.isPlay = true;
      this.timeControl?.play();
    }
  }
  public stopTimeControl(){
    this.timeControl !== undefined && this.timeControl.destroy();
    this.isPlay = false;
  }
  public previousTimeControl(){
    this.timeControl?.previous();
  }
  public nextTimeControl(){
    this.timeControl?.next();
  }


  public async getPointInfo(evt: L.LeafletMouseEvent){
    if (this.isActiveInfoLayers) {
      this.latC = evt.latlng.lat;
      this.lonC = evt.latlng.lng;
      this.isReadyData = false;
      this.template.showDataModal();
      const values = await Promise.all(
        this.activeLayers.map((layer) => this.getFeatureInfo(evt, this.activeURLLayer, layer)));

      if(this.plotClass==="satellite"){
        this.precPlot = this.plotTemplate.pacumPlotTemplate(this.activeDates, values);
      }
      this.isReadyData = true;
    }
  }


  public updateOverlayers(isActiveLayer:boolean, layer:any){
    isActiveLayer ? layer.addTo(this.map) : this.map.removeLayer(layer);
  }

  public updateCanton(){
    const filtered = new Set<string>();
    this.ecuadorData.forEach(item => {
      if (item.provincia === this.selectedProvince) {
        filtered.add(item.canton)}});
    this.cantons = Array.from(filtered);
    this.selectedCanton = this.cantons[0];
  }

  public displayArea(){
    this.selectedCode = this.ecuadorData
          .filter((item) => item.provincia === this.selectedProvince && item.canton === this.selectedCanton)
          .map((item) => item.code)[0];
    const layer = this.selectedCode.endsWith('00') ? "provincias" : "cantones";
    const url = `${environment.urlGeoserver}/ecuador-limits/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=ecuador-limits%3A${layer}&maxFeatures=50&outputFormat=application%2Fjson&CQL_FILTER=DPA_CANTON=${this.selectedCode}`;
    fetch(url)
      .then((response) => response.json())
      .then((data) => {
        this.geojsonLayer && this.map.removeLayer(this.geojsonLayer);
        this.geojsonLayer = L.geoJSON(data, {
          style: { color: '#000000', weight: 1.5, fillOpacity: 0},
        }).addTo(this.map);
        this.map.fitBounds(this.geojsonLayer.getBounds());
      });
  }

  public getAreaInfo(){
    this.isReadyData = false;
    this.template.showDataModal();

    if(this.selectedCode && this.activeLayersCode){
      let encodedLayers = encodeURIComponent(JSON.stringify(this.activeLayersCode));
      let encodedDates = encodeURIComponent(JSON.stringify(this.activeDates));
      let url = `${environment.urlAPI}/metdata/get-metdata?code=${this.selectedCode}&layers=${encodedLayers}&dates=${encodedDates}`;
      fetch(url)
        .then(response => response.json())
        .then(response => {
          const values = response.map((item: any) => item.value);
          if(this.plotClass==="satellite"){
            this.precPlot = this.plotTemplate.pacumPlotTemplate(this.activeDates, values);
          }
          this.isReadyData = true;
        })
    }
  }

}

