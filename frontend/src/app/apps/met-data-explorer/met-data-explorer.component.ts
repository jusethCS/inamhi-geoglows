// TS MODULES AND LIBRARIES
import { CommonModule } from '@angular/common';
import { Component, ViewChild } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule, MatLabel } from '@angular/material/form-field';
import { MatSelect, MatOption, MatSelectModule } from '@angular/material/select';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { FormGroup, FormControl, FormsModule } from '@angular/forms';
import { ReactiveFormsModule, FormBuilder } from '@angular/forms';
import { provideMomentDateAdapter } from '@angular/material-moment-adapter';

// JS LIBRARIES
import * as L from 'leaflet';
import * as PlotlyJS from 'plotly.js-dist-min';
import html2canvas from 'html2canvas';
import { PlotlyModule } from 'angular-plotly.js';
PlotlyModule.plotlyjs = PlotlyJS;

// CUSTOM COMPONENTS AND MODULES
import { AppTemplateComponent } from '../../components/template/app-template.component';
import { DropdownComponent } from '../../components/dropdown/dropdown.component';
import { MapComponent } from "../../components/map/map.component";
import { dataApp } from './met-data-explorer.data';
import { environment } from '../../../environments/environment';
import { Geoserver } from '../../modules/geoserver';
import { WMSTimeControl } from '../../modules/wmsTimeControl';
import { parseGOESDatetime } from '../../modules/datetime';


@Component({
  selector: 'app-met-data-explorer',
  standalone: true,
  imports: [
    AppTemplateComponent,
    CommonModule,
    DropdownComponent,
    MatFormFieldModule,
    MatSelectModule,
    FormsModule,
    MapComponent,
    MatButtonModule
],
  templateUrl: './met-data-explorer.component.html',
  styleUrl: './met-data-explorer.component.css'
})
export class MetDataExplorerComponent {

  @ViewChild('map') map!: MapComponent;
  public dataAppConfig = new dataApp();
  public geoserver = new Geoserver();

  public timeControl: WMSTimeControl | undefined;
  public isPlay:boolean = false;


  // GOES product
  public goesData = this.dataAppConfig.goesData;
  public goesProducts: string[] = this.dataAppConfig.goesProducts;
  public goesBands: string[] = [];
  public goesOverlay: string[] = this.dataAppConfig.goesOverlay;
  public selectedGoesProduct: string = this.goesProducts[0];
  public selectedGoesBand: string = "";
  public selectedGoesOverlay: string = this.dataAppConfig.goesOverlay[0];
  public activeGoesProduct: string = "";
  public activeGoesBand:string = "";
  public activeGoesOverlay:string = "";
  public isAutoUpdateGoes: boolean = false;
  public autoUpdateGoesFun: any;


  ngOnInit() {
    this.updateGoesBand();
  }

  public updateGoesBand() {
    this.goesBands = Array.from(
      new Set(
        this.goesData
          .filter(item => item.Product === this.selectedGoesProduct)
          .map(item => item.Band)));
    this.selectedGoesBand = this.goesBands[0];
  }

  public async updateGoesLayer(){
    this.isPlay = false;
    const workspace = "satellite_data";
    const store = "goes_abi_l2_cmipf_13";
    const url = `${environment.urlGeoserver}/${workspace}/wms`;
    const layers = await this.geoserver.getAvailableDatesFromImageMosaic(url, store);
    const dates = parseGOESDatetime(layers);
    const wmsLayers = layers.map((layer) => this.geoserver.getWMSFromImageMosaic(url, `${workspace}:${store}`, layer))
    console.log(wmsLayers);




    if (this.selectedGoesOverlay !== "None"){
      const overlay = this.goesData.filter(
        (item) => item.Product === this.selectedGoesOverlay)[0].Code;
      const wmsOverlays = layers.map((layer) => this.geoserver.getWMSFromImageMosaic(url, `${workspace}:${overlay}`, layer))
      this.timeControl?.destroy();
      this.timeControl = new WMSTimeControl(this.map.map, wmsLayers, wmsOverlays, "", dates, true);

    }else{
      this.timeControl?.destroy();
      this.timeControl = new WMSTimeControl(this.map.map, wmsLayers, undefined, "", dates, true);
    }

    /**
    const layers = await this.geoserver.getLastLayers(`${url}?service=WMS&request=GetCapabilities`, 10);
    const wmsLayers = layers.map((layer) => this.geoserver.getWMSLayer(url, layer));
    let img = layerCode === "GOES-RGB-TRUE-COLOR" ? undefined : `assets/legend/${layerCode}.png`;

    // Legend text
    const dates = parseGOESDatetime(layers);
    const unitLayer = this.goesData.filter(
      (item) =>
        item.Product === this.selectedGoesProduct &&
        item.Band === this.selectedGoesBand
    )[0].Tag;
    const band = this.selectedGoesBand.replace("Banda", "BANDA").replace(":", ":</b>")
    let legendText = dates.map((item) => `
      <b><b>${this.selectedGoesProduct.toUpperCase()} ${unitLayer}</b></b><br>
      <b>${band}<b><br>
      FECHA:</b> ${item}`)
    if(this.selectedGoesProduct === "Custom RGB Products"){
      legendText = dates.map((item) => `
      <b>PRODUCTO RGB:</b>${this.selectedGoesBand.toUpperCase()}<br>
      <b>FECHA:</b> ${item}`)
    }

    if (this.selectedGoesOverlay !== "None"){
      const layerCodeOverlay = this.goesData.filter(
        (item) => item.Product === this.selectedGoesOverlay)[0].Code;
      const urlOverlay = `${environment.urlGeoserver}/${layerCodeOverlay}/wms`;
      const wmsOverlay = layers.map((layer) => this.geoserver.getWMSLayer(urlOverlay, layer));
      this.timeControl?.destroy();
      this.timeControl = new WMSTimeControl(this.map.map, wmsLayers, wmsOverlay, img, legendText, true)
    } else {
      this.timeControl?.destroy();
      this.timeControl = new WMSTimeControl(this.map.map, wmsLayers, undefined, img, legendText, true)
    }
  */

  }



  public playTimeControl(){
    if (this.isPlay) {
      this.isPlay = false;
      this.timeControl?.pause();
    } else {
      this.isPlay = true;
      this.timeControl?.play();
    }
  }
  public previousTimeControl(){
    this.timeControl?.previous();
  }
  public nextTimeControl(){
    this.timeControl?.next();
  }
  public stopTimeControl(){
    this.timeControl !== undefined && this.timeControl.destroy();
    this.isPlay = false;
  }








}
