import { CommonModule } from '@angular/common';
import { Component, ViewChild } from '@angular/core';

import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule, MatLabel } from '@angular/material/form-field';
import { MatSelect, MatOption } from '@angular/material/select';
import { MatDatepickerModule } from '@angular/material/datepicker';
import {MatSlideToggleModule} from '@angular/material/slide-toggle';
import { FormGroup, FormControl, FormsModule, ReactiveFormsModule, FormBuilder } from '@angular/forms';

import { AppTemplateComponent } from '../../shared/app-template/app-template.component';
import { DropdownComponent } from "../../shared/dropdown/dropdown.component";
import { date_custom_format, satelliteProducts, forecastProduct, GOES, ecuador } from './met-data-explorer.variables';
import { WMSLayerTimeControl } from '../../shared/classes/time-dimension';
import { translateFrecuency, generateDates } from './met-data-explorer.utils';
import { SatelliteDataService } from '../../core/satellite_data.service';
import { LoadingComponent } from "../../shared/loading/loading.component";

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
    ]
})

export class MetDataExplorerComponent {
  // -------------------------------------------------------------------- //
  //                           CLASS ATTRIBUTES                           //
  // -------------------------------------------------------------------- //
  // Template component
  @ViewChild("template") template!: AppTemplateComponent;

  // Leaflet variables
  map: any;

  // Satellite products variables
  vars: string[] = ['Precipitación'];
  prod: string[] = [];
  temp: string[] = [];
  selVars: string = "Precipitación";
  selProd: string = "CHIRPS";
  selTemp: string = "Diario"
  dateRange: FormGroup = new FormGroup({
    start: new FormControl<Date | null>(null),
    end: new FormControl<Date | null>(null),
  });

  // Forecast variables
  forecastModel: string[] = ["WRF", "GFS"]
  forecastVariables: string[] = [];
  selForecastModel: string = "WRF";
  selForecastVariable: string = "Precipitación";

  // GOES
  GOESType: string[] = ["Banda individual", "Composición multiespectral", "Personalizado"];
  GOESProduct: string[] = [];
  selGOESType: string = "Banda individual";
  selGOESProduct: string = 'Banda 1: 0.47 µm ("Blue")';
  activeGOESCustom: boolean = false;
  selGOESCustomBandB: string = 'Banda 1: 0.47 µm ("Blue")';
  selGOESCustomBandR: string = 'Banda 2: 0.64 µm ("Red")';
  selGOESCustomBandG: string = 'Banda 3: 0.86 µm ("Veggie")';
  GOESBands: string[] = [...new Set(
    GOES.filter(
      item => item.Type === "Banda individual"
    ).map(item => item.Producto))];


  // Filters and plots
  prov: string[] = [
    "AZUAY", "BOLIVAR", "CAÑAR", "CARCHI", "COTOPAXI", "CHIMBORAZO", "EL ORO",
    "ESMERALDAS", "GUAYAS", "IMBABURA", "LOJA", "LOS RIOS", "MANABI", "MORONA SANTIAGO",
    "NAPO", "PASTAZA", "PICHINCHA", "TUNGURAHUA", "ZAMORA CHINCHIPE", "GALAPAGOS",
    "SUCUMBIOS", "ORELLANA", "SANTO DOMINGO", "SANTA ELENA"
  ];
  cant: string[] = [];
  selProv: string = "AZUAY";
  selCant: string = "";
  codeArea: string = "";

  // GeoJSON data
  geojson_data: any;
  LGeoJson: any;

  // Leaflet layer - time control
  timeControl: WMSLayerTimeControl | undefined;

  // Plots templates
  precPlot:any = {};
  tempPlot:any = {};
  isReadyData: boolean = false;




  // -------------------------------------------------------------------- //
  //                          CLASS CONSTRUCTOR                           //
  // -------------------------------------------------------------------- //

  constructor( private fb: FormBuilder, private CTservice: SatelliteDataService ) {
    this.updateProduct();
    this.updateTemporal();
    this.initFormDate();
    this.updateForecatVariable();
    this.updateGOESProduct();
    this.updateCanton();
  }

  ngOnInit() {
    this.map = L.map("map");
    this.map.setView([-1.7, -78.5], 7)
    L.tileLayer(
      'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
    ).addTo(this.map);
    setTimeout(() => { this.map.invalidateSize() }, 10);
  }



  // -------------------------------------------------------------------- //
  //                         CLASS METHODS - UI                           //
  // -------------------------------------------------------------------- //
  resizeMap(){
    setTimeout(() => { this.map.invalidateSize() }, 10);
  }

  // Update state for Product selector
  updateProduct() {
    this.prod = [...new Set(
      satelliteProducts.filter(
        item => item.Variable === this.selVars
      ).map(item => item.Producto))];
    this.selProd = this.prod[0];
  }
   // Update state for Temporal selector
   updateTemporal() {
    this.temp = [...new Set(
      satelliteProducts.filter(
        item => item.Variable === this.selVars && item.Producto === this.selProd
      ).map(item => item.Temporalidad))];
    this.selTemp = this.temp[0];
  }

  // Update canton selector
  updateCanton() {
    this.cant = [...new Set(
      ecuador.filter(
        item => item.provincia === this.selProv
      ).map(item => item.canton)
    )];
    this.selCant = this.cant[0];
  }

  // Init datepicker dates
  initFormDate(): void {
    const today = new Date();
    const startDate = new Date(today.getFullYear(), today.getMonth() - 1, 1);
    const endDate = new Date(today.getFullYear(), today.getMonth(), 0);
    this.dateRange = this.fb.group({
      start: [startDate],
      end: [endDate]
    });
  }

  // Update forecast variables - WRF/GFS
  updateForecatVariable(): void{
    this.forecastVariables = [...new Set(
      forecastProduct.filter(
        item => item.Model === this.selForecastModel
      ).map(item => item.Variable))];
    this.selForecastVariable = this.forecastVariables[0];
  }

  // Update GOES product
  updateGOESProduct(): void{
    if(this.selGOESType === "Personalizado"){
      this.activeGOESCustom = true;
    } else{
      this.activeGOESCustom = false;
    }
    this.GOESProduct = [...new Set(
      GOES.filter(
        item => item.Type === this.selGOESType
      ).map(item => item.Producto))];
    this.selGOESProduct = this.GOESProduct[0];
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
      version: "1.1.1",
    });
    return (leafletLayer)
  }

  // Update satellite product
  updateSatelliteProduct() {
    let product = this.selProd.toLowerCase();
    let frequency = translateFrecuency(this.selTemp);
    let startDate = this.dateRange.value.start;
    let endDate = this.dateRange.value.end;
    let url = `${environment.urlGeoserver}/${product}-${frequency}/wms`;
    let target_dates = generateDates(startDate, endDate, frequency)
    let target_layers = target_dates.map(date => `${product}-${frequency}:${date}`)
    let layers = target_layers.map(layer => this.getLeafletLayer(url, layer))
    if (this.timeControl !== undefined) {
      this.timeControl.destroy();
    }
    this.timeControl = new WMSLayerTimeControl(
      this.map, L.control, layers, 1000, target_dates, `${product} ${frequency}`, frequency);
  }

  playTimeControl() {
    this.timeControl?.play();
  }

  stopTimeControl() {
    this.timeControl?.stop();
  }

  previousTimeControl() {
    this.timeControl?.previous();
  }

  nextTimeControl() {
    this.timeControl?.next();
  }


  displayCanton() {
    let code = ecuador.filter(
      item => item.provincia === this.selProv && item.canton === this.selCant
    ).map(item => item.code)[0];
    let url = "";
    if (code && code.endsWith("00")) {
      url = `${environment.urlGeoserver}/ecuador-limits/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=ecuador-limits%3Aprovincias&maxFeatures=50&outputFormat=application%2Fjson&CQL_FILTER=DPA_CANTON=${code}`;
    } else {
      url = `${environment.urlGeoserver}/ecuador-limits/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=ecuador-limits%3Acantones&maxFeatures=50&outputFormat=application%2Fjson&CQL_FILTER=DPA_CANTON=${code}`;
    }
    this.codeArea = code;
    fetch(url)
      .then(response => response.json())
      .then(data => {
        this.geojson_data = data;
        if (this.LGeoJson) {
          this.map.removeLayer(this.LGeoJson);
        }
        this.LGeoJson = L.geoJSON(data, {
          style: {
            color: "#000000",
            weight: 1.5,
            fillOpacity: 0
          }
        }).addTo(this.map)
        this.map.fitBounds(this.LGeoJson.getBounds())
      });

  }

  plotData(){
    this.isReadyData = false;
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

        const dates = response.map((item: any) => item.date);
        const values = response.map((item: any) => item.value);

        if(this.selVars === "Precipitación"){
          this.precPlot = {
            data: [{ x: dates, y: values, type: 'bar'}],
            layout: {
              title: "Hietograma",
              autosize: true,
              margin: { l: 50, r: 30, b: 40, t: 50 },
              xaxis: {
                title: '',
                linecolor: "black",
                linewidth: 1,
                showgrid: false,
                showline: true,
                mirror: true,
                ticks: "outside",
                automargin: true,
              },
              yaxis: {
                title: 'Precipitación (mm)',
                linecolor: "black",
                linewidth: 1,
                showgrid: false,
                showline: true,
                mirror: true,
                ticks: "outside",
                automargin: true,
              }
            }
          };
        }

        if(this.selVars === "Temperatura"){
          this.tempPlot = {
            data: [{ x: dates, y: values, type: 'scatter', mode: 'lines'}],
            layout: { autosize: true, xaxis: { title: ''}, yaxis: { title: 'Temperatura (°C)'} }
          };
        }

        this.isReadyData = true;

      },
      error: (err) => {
        alert("El servidor no pudo procesar su solicitud.")
        console.log(err);
      }
    })

  }







}
