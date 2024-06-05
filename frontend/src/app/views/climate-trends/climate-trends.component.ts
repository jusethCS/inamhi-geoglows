import { CommonModule } from '@angular/common';
import { Component, ViewChild } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';


import { MatLabel } from '@angular/material/form-field';



import { AppHeaderComponent } from '../../shared/app-header/app-header.component';

import { MatAccordion, MatExpansionModule } from '@angular/material/expansion';
import { DropdownPanelComponent } from '../../shared/dropdown-panel/dropdown-panel.component';

import { MatSelectModule } from '@angular/material/select';
import { FormGroup, FormControl, FormsModule, ReactiveFormsModule, FormBuilder } from '@angular/forms';
import { JsonPipe } from '@angular/common';

import { satelliteProducts, date_custom_format, ecuador } from './climate-trends.variables';
import { WMSLayerTimeControl } from '../../shared/classes/time-dimension';

import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatFormFieldModule } from '@angular/material/form-field';
import { provideMomentDateAdapter } from '@angular/material-moment-adapter';


import { ClimateTrendsService } from './climate-trends.service';
import { ModalComponent } from '../../shared/modal/modal.component';
import { LoadingComponent } from '../../shared/loading/loading.component';

import * as L from 'leaflet';


import * as PlotlyJS from 'plotly.js-dist-min';
import { PlotlyModule } from 'angular-plotly.js';
PlotlyModule.plotlyjs = PlotlyJS;


interface ExtendedWMSOptions extends L.WMSOptions {
  CQL_FILTER?: string;
}

@Component({
  selector: 'app-climate-trends',
  standalone: true,
  templateUrl: './climate-trends.component.html',
  styleUrl: './climate-trends.component.css',
  imports: [
    AppHeaderComponent,
    CommonModule,
    PlotlyModule,
    MatExpansionModule,
    MatAccordion,
    DropdownPanelComponent,
    MatLabel,
    MatSelectModule,
    FormsModule,
    MatFormFieldModule,
    MatDatepickerModule,
    FormsModule,
    ReactiveFormsModule,
    JsonPipe,
    MatButtonModule,
    ModalComponent,
    LoadingComponent
  ],
  providers: [provideMomentDateAdapter(date_custom_format)],
})


export class ClimateTrendsComponent {

  // -------------------------------------------------------------------- //
  //                           CLASS ATTRIBUTES                           //
  // -------------------------------------------------------------------- //

  // Leaflet variables
  map: any;

  // State variable for panel activation
  panelActive: boolean = true;

  // Satellite products
  vars: string[] = ['Precipitación'];//, 'Temperatura'];
  prod: string[] = [];
  temp: string[] = [];

  selVars: string = "Precipitación";
  selProd: string = "CHIRPS";
  selTemp: string = "Diario"

  tabla = satelliteProducts;
  tablaEcuador = ecuador;
  dateRange: FormGroup = new FormGroup({
    start: new FormControl<Date | null>(null),
    end: new FormControl<Date | null>(null),
  });
  timeControl: WMSLayerTimeControl | undefined;
  codeArea:string = "";

  // Province and cantons
  prov: string[] = [
    "AZUAY", "BOLIVAR", "CAÑAR", "CARCHI", "COTOPAXI", "CHIMBORAZO", "EL ORO",
    "ESMERALDAS", "GUAYAS", "IMBABURA", "LOJA", "LOS RIOS", "MANABI", "MORONA SANTIAGO",
    "NAPO", "PASTAZA", "PICHINCHA", "TUNGURAHUA", "ZAMORA CHINCHIPE", "GALAPAGOS",
    "SUCUMBIOS", "ORELLANA", "SANTO DOMINGO", "SANTA ELENA"
  ];
  cant: string[] = [];
  selProv: string = "";
  selCant: string = "";

  // GeoJSON data
  geojson_data: any;
  LGeoJson: any;

  // Modals
  @ViewChild(ModalComponent) modalComponent: ModalComponent | undefined;

  // Plots templates
  public precPlot:any = {};
  public tempPlot:any = {};
  isReadyData: boolean = false;


  // -------------------------------------------------------------------- //
  //                          CLASS CONSTRUCTOR                           //
  // -------------------------------------------------------------------- //
  constructor(private fb: FormBuilder, private CTservice: ClimateTrendsService) {
    this.updateProduct();
    this.updateTemporal();
  }

  ngOnInit() {
    // Initialize the map
    this.map = L.map("map");
    this.map.setView([-1.7, -78.5], 7)
    L.tileLayer(
      'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
    ).addTo(this.map);

    // Intialize the datepicker
    this.initFormDate();
  }

  // -------------------------------------------------------------------- //
  //                            CLASS METHODS                             //
  // -------------------------------------------------------------------- //

  // Open or close panel
  isPanelActive(panelActivateEvent: boolean) {
    this.panelActive = panelActivateEvent;
    setTimeout(() => { this.map.invalidateSize() }, 10);
  }

  // Update state for Product selector
  updateProduct() {
    this.prod = [...new Set(
      this.tabla.filter(
        item => item.Variable === this.selVars
      ).map(item => item.Producto))];
    this.selProd = this.prod[0];
  }

  // Update state for Temporal selector
  updateTemporal() {
    this.temp = [...new Set(
      this.tabla.filter(
        item => item.Variable === this.selVars && item.Producto === this.selProd
      ).map(item => item.Temporalidad))];
    this.selTemp = this.temp[0];
  }

  // Update canton selector
  updateCanton() {
    this.cant = [...new Set(
      this.tablaEcuador.filter(
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

  // Get satellite product
  translateFrecuency(frecuency: string): string {
    switch (frecuency.toLowerCase()) {
      case "diaria":
        return "daily";
      case "mensual":
        return "monthly";
      case "anual":
        return "annual";
      default:
        return "NA";
    }
  }

  // Generate dates
  generateDates(startDate: Date, endDate: Date, frequency: string): string[] {
    let generatedDates: string[] = [];
    let currentDate: Date = new Date(startDate);

    // Iterate while the current date is less than or equal to the end date
    while (currentDate <= endDate) {
      // Format the current date as "YYYY-MM-DD"
      let formattedDate: string = `${currentDate.getFullYear()}-${(currentDate.getMonth() + 1).toString().padStart(2, '0')}-${currentDate.getDate().toString().padStart(2, '0')}`;
      generatedDates.push(formattedDate);

      // Increment the date based on the specified frequency
      switch (frequency.toLowerCase()) {
        case "daily":
          currentDate.setDate(currentDate.getDate() + 1);
          break;
        case "monthly":
          currentDate.setMonth(currentDate.getMonth() + 1);
          break;
        case "annual":
          currentDate.setFullYear(currentDate.getFullYear() + 1);
          break;
        default:
          throw new Error("Invalid frequency");
      }
    }

    return generatedDates;
  }


  // Get layer
  getLeafletLayer(url: string, layer: string) {
    let temp_layer = L.tileLayer.wms(url, {
      layers: layer,
      format: 'image/png',
      transparent: true,
      version: "1.1.1",
    });
    return (temp_layer)
  }

  // Update satellite product
  updateSatelliteProduct() {
    let product = this.selProd.toLowerCase();
    let frequency = this.translateFrecuency(this.selTemp);
    let startDate = this.dateRange.value.start;
    let endDate = this.dateRange.value.end;
    let url = `http://ec2-3-211-227-44.compute-1.amazonaws.com/geoserver/${product}-${frequency}/wms`;
    console.log(url)
    let target_dates = this.generateDates(startDate, endDate, frequency)
    let target_layers = target_dates.map(date => `${product}-${frequency}:${date}`)
    console.log(target_layers)
    let layers = target_layers.map(layer => this.getLeafletLayer(url, layer))
    if (this.timeControl !== undefined) {
      this.timeControl.destroy();
    }
    this.timeControl = new WMSLayerTimeControl(
      this.map,
      L.control,
      layers,
      500,
      target_dates,
      `${product} ${frequency}`,
      frequency);
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
    let code = this.tablaEcuador.filter(
      item => item.provincia === this.selProv && item.canton === this.selCant
    ).map(item => item.code)[0];

    let url = "";
    if (code && code.endsWith("00")) {
      url = `http://ec2-3-211-227-44.compute-1.amazonaws.com/geoserver/ecuador-limits/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=ecuador-limits%3Aprovincias&maxFeatures=50&outputFormat=application%2Fjson&CQL_FILTER=DPA_CANTON=${code}`;
    } else {
      url = `http://ec2-3-211-227-44.compute-1.amazonaws.com/geoserver/ecuador-limits/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=ecuador-limits%3Acantones&maxFeatures=50&outputFormat=application%2Fjson&CQL_FILTER=DPA_CANTON=${code}`;
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

  openModal() {
    if (this.modalComponent) {
      this.modalComponent.openModal();
    }
  }

  plotData(){
    this.isReadyData = false;
    let product = this.selProd.toLowerCase();
    let frequency = this.translateFrecuency(this.selTemp);
    let startDate = this.dateRange.value.start;
    let endDate = this.dateRange.value.end;
    let target_dates = this.generateDates(startDate, endDate, frequency);
    let startDateS = target_dates[0];
    let endDateS = target_dates[target_dates.length - 1];
    let code = this.codeArea;

    let a = this.CTservice.get_metdata(product, frequency, startDateS, endDateS, code);
    this.openModal();

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
