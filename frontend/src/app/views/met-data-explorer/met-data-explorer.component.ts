import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { AppTemplateComponent } from '../../shared/app-template/app-template.component';
import { DropdownComponent } from "../../shared/dropdown/dropdown.component";
import { MatButtonModule } from '@angular/material/button';

import { MatFormFieldModule, MatLabel } from '@angular/material/form-field';
import { MatSelect, MatOption } from '@angular/material/select';
import { MatDatepickerModule } from '@angular/material/datepicker';
import {MatSlideToggleModule} from '@angular/material/slide-toggle';

import { FormGroup, FormControl, FormsModule, ReactiveFormsModule, FormBuilder } from '@angular/forms';
import { date_custom_format, satelliteProducts, forecastProduct, GOES, ecuador } from './met-data-explorer.variables';


import { provideMomentDateAdapter } from '@angular/material-moment-adapter';

import * as L from 'leaflet';
import { faL } from '@fortawesome/free-solid-svg-icons';





@Component({
    selector: 'app-met-data-explorer',
    standalone: true,
    templateUrl: './met-data-explorer.component.html',
    styleUrl: './met-data-explorer.component.css',
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
        MatSlideToggleModule
    ],
    providers: [provideMomentDateAdapter(date_custom_format)]
})

export class MetDataExplorerComponent {
  // -------------------------------------------------------------------- //
  //                           CLASS ATTRIBUTES                           //
  // -------------------------------------------------------------------- //
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




  // -------------------------------------------------------------------- //
  //                          CLASS CONSTRUCTOR                           //
  // -------------------------------------------------------------------- //

  constructor( private fb: FormBuilder ) {
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
  //                            CLASS METHODS                             //
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

  displayCanton(){

  }
  plotData(){

  }







}
