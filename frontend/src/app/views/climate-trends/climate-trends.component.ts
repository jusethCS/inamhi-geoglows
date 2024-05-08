import { Component } from '@angular/core';
import { AppHeaderComponent } from '../../shared/components/app-header/app-header.component';
import { CommonModule } from '@angular/common';
import { MatAccordion, MatExpansionModule } from '@angular/material/expansion';
import { DropdownPanelComponent } from '../../shared/components/dropdown-panel/dropdown-panel.component';
import { MatLabel } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { FormGroup, FormControl, FormsModule, ReactiveFormsModule, FormBuilder } from '@angular/forms';
import {JsonPipe} from '@angular/common';

import { satelliteProducts, date_custom_format } from './climate-trends.variables';
import { WMSLayerTimeControl } from '../../shared/classes/time-dimension';

import * as _moment from 'moment';
import {default as _rollupMoment} from 'moment';
import {MatDatepickerModule} from '@angular/material/datepicker';
import {MatFormFieldModule} from '@angular/material/form-field';
import {provideMomentDateAdapter} from '@angular/material-moment-adapter';
import { MatButtonModule } from '@angular/material/button';

const moment = _rollupMoment || _moment;


@Component({
  selector: 'app-climate-trends',
  standalone: true,
  templateUrl: './climate-trends.component.html',
  styleUrl: './climate-trends.component.css',
  imports: [
    AppHeaderComponent,
    CommonModule,
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
    MatButtonModule
  ],
  providers: [provideMomentDateAdapter(date_custom_format)],
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

  // Satellite products
  vars: string[] = ['Precipitación', 'Temperatura'];
  prod: string[] = [];
  temp: string[] = [];
  selVars: string = "Precipitación";
  selProd: string = "CHIRPS";
  selTemp: string = "Diario"
  tabla = satelliteProducts;
  dateRange: FormGroup = new FormGroup({
    start: new FormControl<Date | null>(null),
    end: new FormControl<Date | null>(null),
  });
  timeControl: WMSLayerTimeControl | undefined;


  // -------------------------------------------------------------------- //
  //                          CLASS CONSTRUCTOR                           //
  // -------------------------------------------------------------------- //
  constructor(private fb: FormBuilder) {
    this.updateProduct();
    this.updateTemporal();
  }

  async ngOnInit() {
    // Dinamically import Leaflet
    this.L = await import('leaflet');

    // Initialize the map
    this.map = this.L.map("map");
    this.map.setView([-1.7, -78.5], 7)
    this.L.tileLayer(
      'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
    ).addTo(this.map);

    // Intialize the datepicker
    this.initFormDate();
  }

  // -------------------------------------------------------------------- //
  //                            CLASS METHODS                             //
  // -------------------------------------------------------------------- //

  // Open or close panel
  isPanelActive(panelActivateEvent: boolean){
    this.panelActive = panelActivateEvent;
    setTimeout(() => {this.map.invalidateSize()}, 10);
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
            return "yearly";
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
            case "yearly":
                currentDate.setFullYear(currentDate.getFullYear() + 1);
                break;
            default:
                throw new Error("Invalid frequency");
        }
    }

    return generatedDates;
}


  // Get layer
  getLeafletLayer(url:string, layer:string){
    let temp_layer = this.L.tileLayer.wms(url, {
        layers: layer,
        format: 'image/png',
        transparent: true,
        version: "1.1.1",
      });
    return(temp_layer)
  }

  // Update satellite product
  updateSatelliteProduct(){
    let product = this.selProd.toLowerCase();
    let frequency = this.translateFrecuency(this.selTemp);
    let startDate = this.dateRange.value.start;
    let endDate = this.dateRange.value.end;
    let url = `http://ec2-3-211-227-44.compute-1.amazonaws.com/geoserver/${product}-${frequency}/wms`;
    let target_dates = this.generateDates(startDate, endDate, frequency)
    let target_layers = target_dates.map(date => `${product}-${frequency}:${date}`)
    let layers = target_layers.map(layer => this.getLeafletLayer(url, layer))
    if (this.timeControl !== undefined) {
      this.timeControl.destroy();
    }
    this.timeControl = new WMSLayerTimeControl(this.map, this.L.control, layers, 1000, target_dates);
  }

  playTimeControl(){
    this.timeControl?.play();
  }

  stopTimeControl(){
    this.timeControl?.stop();
  }

  previousTimeControl(){
    this.timeControl?.previous();
  }

  nextTimeControl(){
    this.timeControl?.next();
  }
}
