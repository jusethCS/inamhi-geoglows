import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { AppTemplateComponent } from '../../shared/app-template/app-template.component';
import { DropdownComponent } from "../../shared/dropdown/dropdown.component";
import { MatButtonModule } from '@angular/material/button';

import { MatFormFieldModule, MatLabel } from '@angular/material/form-field';
import { MatSelect, MatOption } from '@angular/material/select';
import { MatDatepickerModule } from '@angular/material/datepicker';

import { FormGroup, FormControl, FormsModule, ReactiveFormsModule, FormBuilder } from '@angular/forms';
import { date_custom_format, satelliteProducts } from './met-data-explorer.variables';


import { provideMomentDateAdapter } from '@angular/material-moment-adapter';

import * as L from 'leaflet';




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
        ReactiveFormsModule
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



  // -------------------------------------------------------------------- //
  //                          CLASS CONSTRUCTOR                           //
  // -------------------------------------------------------------------- //

  constructor( private fb: FormBuilder ) {
    this.updateProduct();
    this.updateTemporal();
    this.initFormDate();
  }

  ngOnInit() {
    this.map = L.map("map");
    this.map.setView([-1.7, -78.5], 7)
    L.tileLayer(
      'https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}{r}.png'
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

}
