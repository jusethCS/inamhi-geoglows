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
import { WMSLayerTimeControl } from '../../shared/classes/time-dimension';
import { AppTemplateComponent } from '../../shared/app-template/app-template.component';
import { DropdownComponent } from '../../shared/dropdown/dropdown.component';
import { LoadingComponent } from '../../shared/loading/loading.component';
import { environment } from '../../../environments/environment';
import { providers } from './modules/providers';
import { dataApp } from './modules/appConfig';
import { utils } from './modules/utils';
import { plotTemplates } from "./modules/plotTemplates";



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

export class ClimateTrendsComponent {
  // Components variables
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

  // GOES product
  public goesData = this.dataAppConfig.goesData;
  public goesProducts: string[] = this.dataAppConfig.goesProducts;
  public selectedGoesProduct: string = this.goesProducts[0];
  public goesBands: string[] = [];
  public selectedGoesBand: string = "";
  public isAutoUpdateGoes: boolean = false;
  public autoUpdateGoesFun: any;

  // Meteorological modeling
  public forecastData = this.dataAppConfig.forecastData;
  public forecastModels: string[] = this.dataAppConfig.forecastModels;
  public selectedForecastModel: string = this.forecastModels[0];
  public forecastVariables: string[] = [];
  public selectedForecastVariable: string = "";
  public forecastTemporals: string[] = [];
  public selectedForecastTemporal: string = "";

  // Layer information and plot
  public timeControl: WMSLayerTimeControl | undefined;
  public isActiveInfoLayers:boolean = false;
  public isPointPlotClass:boolean = false;
  public activeURLLayer: string = '';
  public activeLayers: string[] = [];
  public activeDates: string[] = [];
  public isReadyData: boolean = false;
  public plotClass: string = "satellite"; //goes, wrf,
  public goesBTemp:boolean = false;

  // Plot templates
  public precPlot: any = {};
  public tempPlot: any = {};
  public humPlot: any = {};
  public windPlot: any = {};
  public goesGrayPlot: any = {};
  public goesBTPlot: any = {};

  // Point plot
  latC: any;
  lonC: any;

  // Time control Layers
  public isPlay:boolean = false;


  constructor(
    private formBuilder: FormBuilder,
  ){}

  ngOnInit() {
    this.initializeMap();
    this.resizeMap();
    this.updateSatelliteProduct();
    this.updateSatelliteTemporal();
    this.initFormDate();
    this.updateGoesBand();
    this.updateForecatVariable();
    this.updateForecastTemporal();
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
    const esri = L.tileLayer(
      'https://server.arcgisonline.com/ArcGIS/rest/services/World_Physical_Map/MapServer/tile/{z}/{y}/{x}', {
        zIndex: -1
      });
    const baseMaps = {
      "Mapa claro": osm,
      'Mapa oscuro': carto,
      "Topografico": esri
    };

    // Overlayers
    const cities = L.tileLayer('https://tiles.stadiamaps.com/tiles/stamen_toner_labels/{z}/{x}/{y}{r}.png');
    const provLimits = L.tileLayer.wms(`${environment.urlGeoserver}/ecuador-limits/wms?`, {
          layers: 'ecuador-limits:provincias',
          format: 'image/png',
          transparent: true,
          version: '1.1.0'
        });
    const cantLimits = L.tileLayer.wms(`${environment.urlGeoserver}/ecuador-limits/wms?`, {
          layers: 'ecuador-limits:cantones',
          format: 'image/png',
          transparent: true,
          version: '1.1.0'
        });
    const overlayers = {
      "Limites provinciales": provLimits,
      "Limites cantonales": cantLimits,
      "Ciudades principales": cities,
    }

    // Add base map
    this.map = L.map('map', { center: [-1.7, -78.5], zoom: 7, zoomControl: false });
    osm.addTo(this.map);
    cities.addTo(this.map);
    this.map.on('layeradd', function() {
      cantLimits.bringToFront();
      provLimits.bringToFront();
      cities.bringToFront();
    });

    // Add controls
    L.control.layers(baseMaps, overlayers, { position: 'topright' }).addTo(this.map);
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
    this.quitAutoUpdateGoes();
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
    this.activeDates = dates;
    this.plotClass = "satellite";
  }


  public updateGoesBand(){
    const filtered = new Set<string>();
    this.goesData.forEach(item => {
      if (item.Product === this.selectedGoesProduct) {
        filtered.add(item.Band)}});
    this.goesBands = Array.from(filtered);
    this.selectedGoesBand = this.goesBands[0];
  }

  public async updateGoesLayer(){
    this.isPlay = false;
    let layerCode = this.goesData.filter(
      (item) =>
        item.Product === this.selectedGoesProduct &&
        item.Band === this.selectedGoesBand
    )[0].Code;
    let url = `${environment.urlGeoserver}/${layerCode}/wms`;
    let img = `assets/img/${layerCode}.png`;
    let layers = await this.utilsApp.getLastLayers(`${url}?service=WMS&request=GetCapabilities`, 10);
    console.log(layers);
    let dates = this.utilsApp.parseGOESDate(layers);
    console.log(dates);
    let wmsLayers = layers.map((layer) => this.getLeafletLayer(url, layer));
    if (this.timeControl !== undefined) {
      this.timeControl.destroy();
    }
    this.timeControl = new WMSLayerTimeControl(this.map, L.control, wmsLayers, 250, dates, layerCode, img);

    // Status plot
    this.activeURLLayer = url;
    this.activeLayers = wmsLayers.map(layer => layer.options.layers);
    this.activeDates = dates;
    this.plotClass = "goes";
  }

  public autoUpdateGoes(){
    if(this.isAutoUpdateGoes){
      this.autoUpdateGoesFun = setInterval(() => {
        this.updateGoesLayer().then(() => this.playTimeControl());
      }, 60000);
    }else{
      if (this.autoUpdateGoesFun) {
        clearInterval(this.autoUpdateGoesFun);
      }
    }
  }
  public quitAutoUpdateGoes(){
    this.isAutoUpdateGoes = false;
    if (this.autoUpdateGoesFun) {
      clearInterval(this.autoUpdateGoesFun);
    }
  }

  public updateForecatVariable(){
    const filtered = new Set<string>();
    this.forecastData.forEach(item => {
      if (item.Model === this.selectedForecastModel) {
        filtered.add(item.Variable)}});
    this.forecastVariables = Array.from(filtered);
    this.selectedForecastVariable = this.forecastVariables[0];
  }

  public updateForecastTemporal(){
    const filtered = new Set<string>();
    this.forecastData.forEach(item => {
      if (item.Model === this.selectedForecastModel && item.Variable === this.selectedForecastVariable) {
        filtered.add(item.Temporal)}});
    this.forecastTemporals = Array.from(filtered);
    this.selectedForecastTemporal = this.forecastTemporals[0];
  }

  public async updateForecastLayer(){
    this.quitAutoUpdateGoes();
    this.isPlay = false;
    const layerCode = this.forecastData.filter(
      (item) =>
        item.Model === this.selectedForecastModel &&
        item.Variable === this.selectedForecastVariable &&
        item.Temporal === this.selectedForecastTemporal
    )[0].Code;
    const url = `${environment.urlGeoserver}/${layerCode}/wms`;
    const initForecastDate = this.utilsApp.getInitForecastDate();
    let timestep: string;
    if(this.selectedForecastTemporal === "Diaria"){
      timestep = "24H";
    }else{
      timestep = "3H"
    }
    let layers = await this.utilsApp.getLayersStartWidth(url, `${initForecastDate}-${timestep}`);
    if(layers.length === 0){
      const initForecastDateLast = this.utilsApp.getInitForecastDate(false);
      layers = await this.utilsApp.getLayersStartWidth(url, `${initForecastDateLast}-${timestep}`);
    }
    const img = `assets/img/${layerCode}.png`;
    const title = `Pronóstico de ${this.selectedForecastVariable} (${this.selectedForecastModel})`
    const layerTags = layers.map(layer => `<br>${this.utilsApp.formatForecastDate(layer)}`);
    let wmsLayers = layers.map((layer) => this.getLeafletLayer(url, layer));
    if (this.timeControl !== undefined) {
      this.timeControl.destroy();
    }
    this.timeControl = new WMSLayerTimeControl(this.map, L.control, wmsLayers, 250, layerTags, title, img);

    // Status plot
    this.activeURLLayer = url;
    this.activeLayers = wmsLayers.map(layer => layer.options.layers);
    this.activeDates = layers.map(layer => this.utilsApp.formatForecastDatePlot(layer));;
    this.plotClass = "forecast";
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
    if (this.timeControl !== undefined) {
      this.timeControl.destroy();
    }
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

      if(this.plotClass==="goes"){
        this.goesBTPlot = this.plotTemplate.goesTempPlotTemplate(this.activeDates, values);
        this.goesGrayPlot = this.plotTemplate.goesGrayPlotTemplate(this.activeDates, values);
      }

      if(this.plotClass==="forecast"){
        this.precPlot = this.plotTemplate.pacumPlotTemplate(this.activeDates, values);
        this.tempPlot = this.plotTemplate.tempPlotTemplate(this.activeDates, values);
        this.humPlot = this.plotTemplate.hrPlotTemplate(this.activeDates, values);
        this.windPlot = this.plotTemplate.windPlotTemplate(this.activeDates, values);
      }
      this.isReadyData = true;
      console.log(values);
      console.log(this.activeDates);
    }
  }
}


// YYYYMMDD00Z-24H-YYYYMMDDHHMM
// YYYYMMDD00Z-03H-YYYYMMDDHHMM
