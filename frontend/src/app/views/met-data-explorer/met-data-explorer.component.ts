import { CommonModule } from '@angular/common';
import { Component, ViewChild } from '@angular/core';

import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule, MatLabel } from '@angular/material/form-field';
import { MatSelect, MatOption } from '@angular/material/select';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { FormGroup, FormControl, FormsModule, ReactiveFormsModule, FormBuilder } from '@angular/forms';

import { AppTemplateComponent } from '../../shared/app-template/app-template.component';
import { DropdownComponent } from "../../shared/dropdown/dropdown.component";
import { date_custom_format, satelliteProducts, forecastProduct, GOES, ecuador } from './met-data-explorer.variables';
import { WMSLayerTimeControl } from '../../shared/classes/time-dimension';
import { translateFrecuency, generateDates, convertToCSV, downloadFile } from './met-data-explorer.utils';
import { buildUrl, generateDatesGOES1, generateDatesGOES2, convertToPlotlyFormat } from './met-data-explorer.utils';
import { pacum_plot, temp_plot, goes_temp_plot, goes_gray_plot } from './met-data-explorer.plot-templates';
import { SatelliteDataService } from '../../core/satellite_data.service';
import { LoadingComponent } from "../../shared/loading/loading.component";

import { AuthService } from '../../auth/auth.service';
import { environment } from '../../../environments/environment';
import { provideMomentDateAdapter } from '@angular/material-moment-adapter';


import * as L from 'leaflet';
import * as PlotlyJS from 'plotly.js-dist-min';
import { PlotlyModule } from 'angular-plotly.js';

PlotlyModule.plotlyjs = PlotlyJS;




@Component({
  selector: 'app-met-data-explorer',
  standalone: true,
  templateUrl: './met-data-explorer.component.html',
  styleUrl: './met-data-explorer.component.css',
  providers: [provideMomentDateAdapter(date_custom_format)],
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
export class MetDataExplorerComponent {
  // -------------------------------------------------------------------- //
  //                           CLASS ATTRIBUTES                           //
  // -------------------------------------------------------------------- //
  // Template component
  @ViewChild('template') template!: AppTemplateComponent;
  public isAuth: boolean = false;

  // Leaflet variables
  map: any;

  // Satellite products variables
  vars: string[] = ['Precipitación'];
  prod: string[] = [];
  temp: string[] = [];
  selVars: string = 'Precipitación';
  selProd: string = 'CHIRPS';
  selTemp: string = 'Diario';
  dateRange: FormGroup = new FormGroup({
    start: new FormControl<Date | null>(null),
    end: new FormControl<Date | null>(null),
  });

  // Forecast variables
  forecastModel: string[] = ['WRF', 'GFS'];
  forecastVariables: string[] = [];
  selForecastModel: string = 'WRF';
  selForecastVariable: string = 'Precipitación';

  // GOES
  GOESProduct: string[] = ['Cloud and Moisture Imagery', 'Personalizado'];
  GOESBand: string[] = [];
  selGOESProduct: string = 'Cloud and Moisture Imagery';
  selGOESBand: string = 'Banda 1: 0.47 µm ("Blue")';
  isAutoUpdateGOES: boolean = false;
  updateGOESFun: any;

  // Filters and plots
  prov: string[] = [
    'AZUAY',
    'BOLIVAR',
    'CAÑAR',
    'CARCHI',
    'COTOPAXI',
    'CHIMBORAZO',
    'EL ORO',
    'ESMERALDAS',
    'GUAYAS',
    'IMBABURA',
    'LOJA',
    'LOS RIOS',
    'MANABI',
    'MORONA SANTIAGO',
    'NAPO',
    'PASTAZA',
    'PICHINCHA',
    'TUNGURAHUA',
    'ZAMORA CHINCHIPE',
    'GALAPAGOS',
    'SUCUMBIOS',
    'ORELLANA',
    'SANTO DOMINGO',
    'SANTA ELENA',
  ];
  cant: string[] = [];
  selProv: string = 'AZUAY';
  selCant: string = '';
  codeArea: string = '';

  // GeoJSON data
  geojson_data: any;
  LGeoJson: any;
  meteorological_data: any;
  meteorological_header: any;

  // Leaflet layer - Time control
  timeControl: WMSLayerTimeControl | undefined;
  isPlay: boolean = false;

  // Info Leayers Control
  activeURLLayer: string = '';
  activeLayers: string[] = [];
  activeDates: string[] = [];
  isActiveInfoLayers: boolean = false;

  // Plots templates
  precPlot: any = {};
  tempPlot: any = {};
  goesGrayPlot: any = {};
  goesBTPlot: any = {};
  isReadyData: boolean = false;

  plotClass: string = "satellite"; //goes, wrf,
  isPointPlotClass: boolean = false;
  goesBTemp:boolean = false;

  // Puntual plots request
  latC: any;
  lonC: any;

  // -------------------------------------------------------------------- //
  //                          CLASS CONSTRUCTOR                           //
  // -------------------------------------------------------------------- //

  constructor(
    private fb: FormBuilder,
    private CTservice: SatelliteDataService,
    private authService: AuthService
  ) {
    this.isAuth = this.authService.isAuth();
    this.updateProduct();
    this.updateTemporal();
    this.initFormDate();
    this.updateForecatVariable();
    this.updateGOESBand();
    this.updateCanton();
  }

  ngOnInit() {
    const osm = L.tileLayer(
      'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
      {
        zIndex: -1,
      }
    );

    const carto = L.tileLayer(
      'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
      {
        subdomains: 'abcd',
        maxZoom: 20,
        zIndex: -1,
      }
    );

    const baseMaps = {
      OpenStreetMap: osm.bringToBack(),
      'Carto DarkMap': carto.bringToBack(),
    };

    this.map = L.map('map', {
      center: [-1.7, -78.5],
      zoom: 7,
      zoomControl: false,
    });
    osm.addTo(this.map);

    L.control.layers(baseMaps, {}, { position: 'topright' }).addTo(this.map);
    L.control.zoom({ position: 'topright' }).addTo(this.map);

    const imageElement = document.createElement('img');
    const logoControl = new L.Control({ position: 'topleft' });
    imageElement.src = 'assets/img/inamhi-white-logo.png';
    imageElement.height = 55;
    imageElement.width = 125;
    logoControl.onAdd = () => imageElement;
    logoControl.addTo(this.map);

    setTimeout(() => {
      this.map.invalidateSize();
    }, 10);

    const infoControl = new L.Control({ position: 'topright' });
    infoControl.onAdd = () => {
      const infoDiv = document.createElement('div');
      infoDiv.innerHTML =
        `<div class="d-flex justify-content-center align-items-center">
          <i class="fa-regular fa-circle-info"></i>
        </div>`;
      infoDiv.style.minWidth = '33px';
      infoDiv.style.minHeight = '33px';
      infoDiv.style.backgroundColor = 'white';
      infoDiv.style.borderRadius = '4px';
      infoDiv.style.fontSize = '22px';
      infoDiv.style.lineHeight = '1.5';
      infoDiv.style.border = '2px solid rgba(0,0,0,0.2)';
      infoDiv.style.backgroundClip = 'padding-box';
      infoDiv.style.paddingTop = '4px';
      infoDiv.style.cursor = 'pointer';

      // Detener la propagación del evento click
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
      return infoDiv;
    };
    infoControl.addTo(this.map);

    this.map.on('click', async (evt: L.LeafletMouseEvent) => {
      this.plotPointData(evt)
    });
  }

  // -------------------------------------------------------------------- //
  //                         CLASS METHODS - UI                           //
  // -------------------------------------------------------------------- //
  resizeMap() {
    setTimeout(() => {
      this.map.invalidateSize();
    }, 10);
  }

  // Update state for Product selector
  updateProduct() {
    this.prod = [
      ...new Set(
        satelliteProducts
          .filter((item) => item.Variable === this.selVars)
          .map((item) => item.Producto)
      ),
    ];
    this.selProd = this.prod[0];
  }
  // Update state for Temporal selector
  updateTemporal() {
    this.temp = [
      ...new Set(
        satelliteProducts
          .filter(
            (item) =>
              item.Variable === this.selVars && item.Producto === this.selProd
          )
          .map((item) => item.Temporalidad)
      ),
    ];
    this.selTemp = this.temp[0];
  }

  // Update canton selector
  updateCanton() {
    this.cant = [
      ...new Set(
        ecuador
          .filter((item) => item.provincia === this.selProv)
          .map((item) => item.canton)
      ),
    ];
    this.selCant = this.cant[0];
  }

  // Init datepicker dates
  initFormDate(): void {
    const today = new Date();
    const startDate = new Date(today.getFullYear(), today.getMonth() - 1, 1);
    const endDate = new Date(today.getFullYear(), today.getMonth(), 0);
    this.dateRange = this.fb.group({
      start: [startDate],
      end: [endDate],
    });
  }

  // Update forecast variables - WRF/GFS
  updateForecatVariable(): void {
    this.forecastVariables = [
      ...new Set(
        forecastProduct
          .filter((item) => item.Model === this.selForecastModel)
          .map((item) => item.Variable)
      ),
    ];
    this.selForecastVariable = this.forecastVariables[0];
  }

  // Update GOES product
  updateGOESBand(): void {
    this.GOESBand = [
      ...new Set(
        GOES.filter((item) => item.Product === this.selGOESProduct).map(
          (item) => item.Band
        )
      ),
    ];
    this.selGOESBand = this.GOESBand[0];
  }

  // -------------------------------------------------------------------- //
  //                      CLASS METHODS - BACKEND                         //
  // -------------------------------------------------------------------- //

  // Function to retrieve the leaflet WMS layer
  getLeafletLayer(url: string, layer: string) {
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

  // Functio to retrieve data from active layers (using a specific point)
  async getFeatureInfo(
    evt: L.LeafletMouseEvent,
    baseUrl: string,
    layer: string
  ) {
    const point = this.map!.latLngToContainerPoint(
      evt.latlng,
      this.map!.getZoom()
    );
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
    const url = buildUrl(baseUrl, params);
    const response = await fetch(url);
    const data = await response.json();
    if (
      data.features &&
      data.features.length > 0 &&
      data.features[0].properties
    ) {
      const grayIndexString = data.features[0].properties.GRAY_INDEX;
      return(grayIndexString);
    }
    return undefined;
  }

  // Update satellite product
  updateSatelliteProduct() {
    this.isPlay = false;
    let product = this.selProd.toLowerCase();
    let frequency = translateFrecuency(this.selTemp);
    let startDate = this.dateRange.value.start;
    let endDate = this.dateRange.value.end;
    let url = `${environment.urlGeoserver}/${product}-${frequency}/wms`;
    let target_dates = generateDates(startDate, endDate, frequency);
    let target_layers = target_dates.map(
      (date) => `${product}-${frequency}:${date}`
    );
    let layers = target_layers.map((layer) => this.getLeafletLayer(url, layer));
    console.log(layers);
    if (this.timeControl !== undefined) {
      this.timeControl.destroy();
    }
    this.timeControl = new WMSLayerTimeControl(
      this.map,
      L.control,
      layers,
      1000,
      target_dates,
      `${product} ${frequency}`,
      `assets/img/pacum-legend-${frequency}.png`
    );

    this.activeURLLayer = url;
    this.activeLayers = target_layers;
    this.activeDates = target_dates;
    this.plotClass = "satellite";
  }

  // Update GOES data
  updateGOES() {
    this.isPlay = false;
    let dateGOES_layer = generateDatesGOES1();
    let dateGOES = generateDatesGOES2();
    let goes_code = [
      ...new Set(
        GOES.filter(
          (item) =>
            item.Product === this.selGOESProduct &&
            item.Band === this.selGOESBand
        ).map((item) => item.Code)
      ),
    ][0];
    let goesBandSelected = [
      ...new Set(
        GOES.filter(
          (item) =>
            item.Product === this.selGOESProduct &&
            item.Band === this.selGOESBand
        ).map((item) => item.B)
      ),
    ][0];
    let url = `${environment.urlGeoserver}/${goes_code}/wms`;
    let target_layers = dateGOES_layer.map((date) => `${goes_code}:${date}`);
    let layers = target_layers.map((layer) => this.getLeafletLayer(url, layer));
    if (this.timeControl !== undefined) {
      this.timeControl.destroy();
    }
    let img = `assets/img/${goes_code}.png`;
    this.timeControl = new WMSLayerTimeControl(
      this.map,
      L.control,
      layers,
      200,
      dateGOES,
      goes_code,
      img
    );

    this.activeURLLayer = url;
    this.activeLayers = target_layers;
    this.activeDates = dateGOES;
    this.plotClass = "goes";
    if(goesBandSelected <= 7){
      this.goesBTemp = false;
    } else{
      this.goesBTemp = true;
    }
  }

  autoUpdateGOES(){
    if(this.isAutoUpdateGOES){
      this.updateGOESFun = setInterval(() => {
        this.updateGOES();
        this.playTimeControl();
        console.log("Actualizacion GOES");
      }, 60000);
    }else{
      if (this.updateGOESFun) {
        clearInterval(this.updateGOESFun);
      }
    }
  }



  playTimeControl() {
    if (this.isPlay) {
      this.isPlay = false;
      this.timeControl?.stop();
    } else {
      this.isPlay = true;
      this.timeControl?.play();
    }
  }

  stopTimeControl() {
    if (this.timeControl !== undefined) {
      this.timeControl.destroy();
    }
    this.isPlay = false;
  }

  previousTimeControl() {
    this.timeControl?.previous();
  }

  nextTimeControl() {
    this.timeControl?.next();
  }




  displayCanton() {
    let code = ecuador
      .filter(
        (item) =>
          item.provincia === this.selProv && item.canton === this.selCant
      )
      .map((item) => item.code)[0];
    let url = '';
    if (code && code.endsWith('00')) {
      url = `${environment.urlGeoserver}/ecuador-limits/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=ecuador-limits%3Aprovincias&maxFeatures=50&outputFormat=application%2Fjson&CQL_FILTER=DPA_CANTON=${code}`;
    } else {
      url = `${environment.urlGeoserver}/ecuador-limits/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=ecuador-limits%3Acantones&maxFeatures=50&outputFormat=application%2Fjson&CQL_FILTER=DPA_CANTON=${code}`;
    }
    this.codeArea = code;
    fetch(url)
      .then((response) => response.json())
      .then((data) => {
        this.geojson_data = data;
        if (this.LGeoJson) {
          this.map.removeLayer(this.LGeoJson);
        }
        this.LGeoJson = L.geoJSON(data, {
          style: {
            color: '#000000',
            weight: 1.5,
            fillOpacity: 0,
          },
        }).addTo(this.map);
        this.map.fitBounds(this.LGeoJson.getBounds());
      });
  }

  plotData() {
    this.isReadyData = false;

    if(this.plotClass === "satellite"){
      let product = this.selProd.toLowerCase();
      let frequency = translateFrecuency(this.selTemp);
      let startDate = this.dateRange.value.start;
      let endDate = this.dateRange.value.end;
      let target_dates = generateDates(startDate, endDate, frequency);
      let startDateS = target_dates[0];
      let endDateS = target_dates[target_dates.length - 1];
      let code = this.codeArea;

      let a = this.CTservice.get_metdata(product, frequency, startDateS, endDateS, code);
      this.template.showDataModal();

      a.subscribe({
        next: (response) => {
          this.meteorological_data = response;
          const dates = response.map((item: any) => item.date);
          const values = response.map((item: any) => item.value);
          if (this.selVars === 'Precipitación') {
            this.meteorological_header = ['Datetime', 'Precipitacion (mm)'];
            this.precPlot = pacum_plot(dates, values);
          }
          if (this.selVars === 'Temperatura') {
            this.meteorological_header = ['Datetime', 'Temperatura (mm)'];
            this.tempPlot = temp_plot(dates, values);
          }
          this.isReadyData = true;
        },
        error: (err) => {
          alert('El servidor no pudo procesar su solicitud.');
          console.log(err);
        },
      });
    }

    if(this.plotClass === "wrf"){
      console.log("wrf")
    }
  }



  async plotPointData(evt: L.LeafletMouseEvent) {

    if (this.isActiveInfoLayers) {
      this.latC = evt.latlng.lat;
      this.lonC = evt.latlng.lng;
      this.isReadyData = false;
      this.template.showDataModal();

      const values = await Promise.all(
        this.activeLayers.map((layer) =>
          this.getFeatureInfo(evt, this.activeURLLayer, layer)
        ));
      const dates = this.activeDates.map((item: any) => convertToPlotlyFormat(item)); //this.activeDates;

      if(this.plotClass === "satellite"){
        if(this.selVars === 'Precipitación'){
          this.meteorological_header = ['Datetime', 'Precipitacion (mm)'];
          this.precPlot = pacum_plot(dates, values);
        }
      }
      if(this.plotClass === "goes"){
        this.goesGrayPlot = goes_temp_plot(dates, values);
        this.goesBTPlot = goes_gray_plot(dates, values);
      }

      console.log(dates);
      console.log(values);

      this.isReadyData = true;

    }
  }



  downloadData() {
    const csvData = convertToCSV(
      this.meteorological_data,
      this.meteorological_header
    );
    downloadFile(csvData, `${this.selProd}.csv`);
  }
}
