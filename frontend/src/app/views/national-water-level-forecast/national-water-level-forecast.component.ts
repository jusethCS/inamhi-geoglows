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
import { dataApp } from './national-water-level-forecast.component.config';



@Component({
  selector: 'app-national-water-level-forecast',
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
    AsyncPipe,
  ],
  templateUrl: './national-water-level-forecast.component.html',
  styleUrl: './national-water-level-forecast.component.css'
})
export class NationalWaterLevelForecastComponent {
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

  // Date Input
  public dateControl = new FormControl(new Date());
  public dateControlPanel = new FormControl(new Date());
  public minDate = new Date('2024-07-22');
  public maxDate = new Date();
  public rangeDate:string[] = [];

  // Flood warnings
  public isActiveFlood000:boolean = true;
  public isActiveFlood002:boolean = true;
  public isActiveFlood005:boolean = true;
  public isActiveFlood010:boolean = true;
  public isActiveFlood025:boolean = true;
  public isActiveFlood050:boolean = true;
  public isActiveFlood100:boolean = true;
  public activeDateIndex:number = 0;
  public geoglowsFloodWarnings:any;
  public geoglowsFlood000:any;
  public geoglowsFlood002:any;
  public geoglowsFlood005:any;
  public geoglowsFlood010:any;
  public geoglowsFlood025:any;
  public geoglowsFlood050:any;
  public geoglowsFlood100:any;
  public legendControl = new L.Control({position: 'bottomleft'});

  // Plots
  public historicalSimulationPlot: any;
  public dailyAveragePlot:any;
  public monthlyAveragePlot:any;
  public flowDurationCurve:any;
  public volumePlot:any;
  public forecastPlot:any;
  public isReadyDataPlot:boolean = false;
  public htmlContent:string = "";

  // Variables for panel
  public comid: string = "";
  public latitude: string = "";
  public longitude: string = "";
  public river: string = "";
  public province: string = "";
  public canton: string = "";

  // Plot - geographical area
  public dataAppConfig = new dataApp();
  public ecuadorData = this.dataAppConfig.ecuador;
  public provinces = this.dataAppConfig.provinces;
  public selectedProvince = this.provinces[0];
  public cantons: string[] = [];
  public selectedCanton: string = "";
  public geojsonLayer!: L.GeoJSON;
  public selectedCode:string = "";
  public geojsonRivers!: L.GeoJSON;

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

  // Base layers
  public citiesLayer: any;
  public provinceLayer: any;
  public cantonLayer:any;
  public protectedAreaLayer:any;
  public waterRechargeLayer:any;
  public conectivityCoLayer:any;
  public hydropowers50Layer:any;
  public hydropowerLayer:any;
  public humedalRamsarLayer:any;
  public reservaBiosferaLayer:any;
  public conservacionSocioBosqueLayer:any;
  public bosqueProtectorLayer:any;
  public SNAPLayer:any;

  public isActiveCitiesLayer:boolean = false;
  public isActiveProvinceLayer: boolean = false;
  public isActiveCantonLayer:boolean = false;
  public isActiveDrainage:boolean = true;
  public isActiveProtectedArea:boolean = false;
  public isActiveWaterRecharge:boolean = false;
  public isActiveConectivityCo:boolean = false;
  public isActiveHydropowers50:boolean = false;
  public isActiveHydropowers:boolean = false;
  public isActiveHumedalRamsar:boolean = false;
  public isActiveReservaBiosfera:boolean = false;
  public isActiveConservacionSocioBosque:boolean = false;
  public isActiveBosqueProtector:boolean = false;
  public isActiveSNAP:boolean = false;



  // Search controls
  public riverNameControl = new FormControl('');
  public riverNameOptions: string[] = [];
  public riverNameFilteredOptions: Observable<string[]> | undefined;
  public comidControl = new FormControl('');
  public comidOptions: string[] = [];
  public comidFilteredOptions: Observable<string[]> | undefined;



  constructor(private renderer: Renderer2) {}


  ngOnInit() {
    this.initializeDate();
    this.initializeMap();
    this.initializeOverlays();
    this.resizeMap();
    this.getFloodWarnings();
    this.updateCanton();
  }



  public initializeRiverNameControl(geojson:any) {
    const riverNames = geojson.features.map((feature:any) => feature.properties.river);
    this.riverNameOptions = riverNames
        .filter((name: unknown, index: any, self: string | string[]) =>
          name &&                      // Eliminar valores vacíos (null, undefined)
          typeof name === 'string' &&  // Asegurar que es una cadena de texto
          name.trim() !== '' &&        // Eliminar cadenas vacías
          !Number.isNaN(name) &&       // Eliminar valores NaN
          self.indexOf(name) === index // Eliminar duplicados
        ).sort((a:string, b:string) => a.localeCompare(b));
    this.riverNameFilteredOptions = this.riverNameControl.valueChanges.pipe(
      startWith(''),
      map(value => {
        const valueSis = (value || '')
        const filterValue = valueSis.toLowerCase();
        return this.riverNameOptions.filter(option => option.toLowerCase().includes(filterValue));
      })
    );
  };

  public initializeComidControl(geojson:any) {
    const comids = geojson.features.map((feature:any) => feature.properties.comid.toString());
    this.comidOptions = comids
      .filter((name: unknown, index: any, self: string | string[]) =>
        name &&                      // Eliminar valores vacíos (null, undefined)
        typeof name === 'string' &&  // Asegurar que es una cadena de texto
        name.trim() !== '' &&        // Eliminar cadenas vacías
        !Number.isNaN(name) &&       // Eliminar valores NaN
        self.indexOf(name) === index // Eliminar duplicados
      ).sort((a:string, b:string) => a.localeCompare(b));

      this.comidFilteredOptions = this.comidControl.valueChanges.pipe(
        startWith(''),
        map(value => {
          const valueSis = (value || '')
          const filterValue = valueSis.toLowerCase();
          return this.comidOptions.filter(option => option.toLowerCase().includes(filterValue));
        })
      );
  };




  public onRiverSelected(selectedRiver: string) {
    console.log('Río seleccionado:', selectedRiver);
    this.geojsonRivers && this.map.removeLayer(this.geojsonRivers);
    const filteredFeatures = this.draingeNetwork.toGeoJSON().features.filter((feature: any) => {
      return feature.properties.river === selectedRiver});
    const data = {
      type: this.draingeNetwork.type,
      features: filteredFeatures};
    this.geojsonRivers = L.geoJSON(data, {style: {weight:4, color:"red"}}).addTo(this.map);
    this.map.fitBounds(this.geojsonRivers.getBounds());
  }

  public onComidSelected(selectedComid: string) {
    console.log('Río seleccionado:', selectedComid);
    this.geojsonRivers && this.map.removeLayer(this.geojsonRivers);
    const filteredFeatures = this.draingeNetwork.toGeoJSON().features.filter((feature: any) => {
      return feature.properties.comid === parseInt(selectedComid, 10)});
    const data = {
      type: this.draingeNetwork.type,
      features: filteredFeatures};
    this.geojsonRivers = L.geoJSON(data, {style: {weight:4, color:"red"}}).addTo(this.map);
    this.map.fitBounds(this.geojsonRivers.getBounds());
  }


  public initializeDate(){
    this.dateControl.setValue(this.maxDate);
    if(this.dateControl.value){
      this.rangeDate = this.utilsApp.getDateRangeGeoglows(this.dateControl.value);
    }
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

    // Add drainage network
    const urlDrainage = `${environment.urlGeoserver}/geoglows/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=geoglows:ecuador_drainage_network_geoglows&outputFormat=application/json`;
    fetch(urlDrainage)
    .then((response) => response.json())
    .then(data => {
      L.geoJSON(data, {style: {weight:0.7, color:"#4747C9"}}).addTo(this.map)
      this.draingeNetwork = L.geoJSON(data, {
          style: {weight: 12, color: "rgba(0, 0, 0, 0)"}
      }).addTo(this.map);
      this.draingeNetwork.on("click", (e: L.LeafletMouseEvent) => this.getParamRiver(e));
      this.initializeRiverNameControl(data);
      this.initializeComidControl(data);
    });

  }

  public initializeOverlays(){
    this.citiesLayer = L.tileLayer(
      'https://tiles.stadiamaps.com/tiles/stamen_toner_labels/{z}/{x}/{y}{r}.png', {
        zIndex: 1100
      });
    //this.citiesLayer.addTo(this.map);
    this.provinceLayer = L.tileLayer.wms(`${environment.urlGeoserver}/ecuador-limits/wms?`, {
      layers: 'ecuador-limits:provincias',
      format: 'image/svg',
      transparent: true,
      version: '1.1.0',
      zIndex: 1000
    });
    //this.provinceLayer.addTo(this.map);
    this.cantonLayer = L.tileLayer.wms(`${environment.urlGeoserver}/ecuador-limits/wms?`, {
      layers: 'ecuador-limits:cantones',
      format: 'image/svg',
      transparent: true,
      version: '1.1.0',
      zIndex: 900
    });
    this.protectedAreaLayer = L.tileLayer.wms(`${environment.urlGeoserver}/ecuador-limits/wms?`, {
      layers: 'ecuador-limits:areas_protegidas',
      format: 'image/svg',
      transparent: true,
      version: '1.1.0',
      zIndex: 900
    });
    this.waterRechargeLayer = L.tileLayer.wms(`${environment.urlGeoserver}/ecuador-limits/wms?`, {
      layers: 'ecuador-limits:zonas_recarga_hidrica',
      format: 'image/svg',
      transparent: true,
      version: '1.1.0',
      zIndex: 900
    });
    this.conectivityCoLayer = L.tileLayer.wms(`${environment.urlGeoserver}/ecuador-limits/wms?`, {
      layers: 'ecuador-limits:corredor_conectividad2',
      format: 'image/svg',
      transparent: true,
      version: '1.1.0',
      zIndex: 900,
    });
    this.hydropowers50Layer = L.tileLayer.wms(`${environment.urlGeoserver}/ecuador-limits/wms?`, {
      layers: 'ecuador-limits:hidroelectricas_mayores_50MW',
      format: 'image/svg',
      transparent: true,
      version: '1.1.0',
      zIndex: 1100,
    });
    this.humedalRamsarLayer = L.tileLayer.wms(`${environment.urlGeoserver}/ecuador-limits/wms?`, {
      layers: 'ecuador-limits:humedal_ramsar',
      format: 'image/svg',
      transparent: true,
      version: '1.1.0',
      zIndex: 1100,
    });
    this.reservaBiosferaLayer = L.tileLayer.wms(`${environment.urlGeoserver}/ecuador-limits/wms?`, {
      layers: 'ecuador-limits:reserva_biosfera',
      format: 'image/svg',
      transparent: true,
      version: '1.1.0',
      zIndex: 1100,
    });
    this.conservacionSocioBosqueLayer = L.tileLayer.wms(`${environment.urlGeoserver}/ecuador-limits/wms?`, {
      layers: 'ecuador-limits:conservacion_socio_bosque',
      format: 'image/svg',
      transparent: true,
      version: '1.1.0',
      zIndex: 1100,
    });
    this.bosqueProtectorLayer = L.tileLayer.wms(`${environment.urlGeoserver}/ecuador-limits/wms?`, {
      layers: 'ecuador-limits:bosque_vegetacion_protectora',
      format: 'image/svg',
      transparent: true,
      version: '1.1.0',
      zIndex: 1100,
    });
    this.SNAPLayer = L.tileLayer.wms(`${environment.urlGeoserver}/ecuador-limits/wms?`, {
      layers: 'ecuador-limits:sistema_nacional_areas_protegidas',
      format: 'image/svg',
      transparent: true,
      version: '1.1.0',
      zIndex: 1100,
    });

    const overlayers = [
      this.cantonLayer, this.provinceLayer,
      this.protectedAreaLayer, this.waterRechargeLayer, this.conectivityCoLayer,
      this.humedalRamsarLayer, this.reservaBiosferaLayer, this.conservacionSocioBosqueLayer,
      this.bosqueProtectorLayer, this.SNAPLayer,
      this.citiesLayer, this.hydropowers50Layer
    ];

    this.map.on('layeradd', function(){
      overlayers.map(layer => layer.bringToFront());
    });
  }

  public updateOverlayers(isActiveLayer:boolean, layer:any){
    isActiveLayer ? layer.addTo(this.map) : this.map.removeLayer(layer);
  }


  private getParamRiver(e: L.LeafletMouseEvent){
    // Conditions
    this.isReadyDataPlot = false;
    this.renderer.setProperty(this.table.nativeElement, 'innerHTML', "");

    // Data
    const prop = e.layer.feature.properties;
    this.comid = prop.comid;
    this.latitude = prop.latitude;
    this.longitude = prop.longitude;
    this.river = prop.river;
    this.province = prop.loc1;
    this.canton = prop.loc2;
    this.dateControlPanel.setValue(this.dateControl.value);

    this.template.showDataModal();
    setTimeout(() => {
      const elementWidth = this.panelPlot.nativeElement.offsetWidth; //this.template.dataModal?.nativeElement.offsetWidth;
      fetch(`${environment.urlAPI}/geoglows/geoglows-data-plot?comid=${this.comid}&date=${this.rangeDate[0]}&width=${elementWidth}`)
      .then((response) => response.json())
      .then((response) => {
        this.historicalSimulationPlot = response.hs;
        this.dailyAveragePlot = response.dp;
        this.monthlyAveragePlot = response.mp;
        this.flowDurationCurve = response.fd;
        this.volumePlot = response.vp;
        this.forecastPlot = response.fp;
        this.isReadyDataPlot = true;
        fetch(`${environment.urlAPI}/geoglows/geoglows-table?comid=${this.comid}&date=${this.rangeDate[0]}`)
          .then((response) => response.text())
          .then((response) => {
            this.renderer.setProperty(this.table.nativeElement, 'innerHTML', response);
          })
      })
    }, 300);
  }

  private getParamAlert(e: L.LeafletMouseEvent){
    // Conditions
    this.isReadyDataPlot = false;
    this.renderer.setProperty(this.table.nativeElement, 'innerHTML', "");

    // Data
    const prop = e.layer.feature.properties;
    this.comid = prop.comid;
    this.latitude = prop.latitude;
    this.longitude = prop.longitude;
    this.river = prop.river;
    this.province = prop.location1;
    this.canton = prop.location2;
    this.dateControlPanel.setValue(this.dateControl.value);

    this.template.showDataModal();
    setTimeout(() => {
      const elementWidth = this.panelPlot.nativeElement.offsetWidth;
      fetch(`${environment.urlAPI}/geoglows/geoglows-data-plot?comid=${this.comid}&date=${this.rangeDate[0]}&width=${elementWidth}`)
      .then((response) => response.json())
      .then((response) => {
        this.historicalSimulationPlot = response.hs;
        this.dailyAveragePlot = response.dp;
        this.monthlyAveragePlot = response.mp;
        this.flowDurationCurve = response.fd;
        this.volumePlot = response.vp;
        this.forecastPlot = response.fp;
        this.isReadyDataPlot = true;
        fetch(`${environment.urlAPI}/geoglows/geoglows-table?comid=${this.comid}&date=${this.rangeDate[0]}`)
          .then((response) => response.text())
          .then((response) => {
            this.renderer.setProperty(this.table.nativeElement, 'innerHTML', response);
          })
      })
    }, 300);
  }

  public updateForecastPlots(){
    // Conditions
    this.isReadyDataPlot = false;
    this.renderer.setProperty(this.table.nativeElement, 'innerHTML', "");
    if(this.dateControlPanel.value){
      const currentDate = this.utilsApp.getDateRangeGeoglows(this.dateControlPanel.value);
      setTimeout(() => {
        const elementWidth = this.panelPlot.nativeElement.offsetWidth;
        fetch(`${environment.urlAPI}/geoglows/geoglows-data-plot?comid=${this.comid}&date=${currentDate[0]}&width=${elementWidth}`)
        .then((response) => response.json())
        .then((response) => {
          this.historicalSimulationPlot = response.hs;
          this.dailyAveragePlot = response.dp;
          this.monthlyAveragePlot = response.mp;
          this.flowDurationCurve = response.fd;
          this.volumePlot = response.vp;
          this.forecastPlot = response.fp;
          this.isReadyDataPlot = true;
          fetch(`${environment.urlAPI}/geoglows/geoglows-table?comid=${this.comid}&date=${currentDate[0]}`)
            .then((response) => response.text())
            .then((response) => {
              this.renderer.setProperty(this.table.nativeElement, 'innerHTML', response);
            })
        })
      }, 300);
    }
  }

  public resizeMap(): void {
    setTimeout(() => { this.map.invalidateSize() }, 10);
  }

  public getFloodWarnings(){
    const url = `${environment.urlAPI}/geoglows/geoglows-waterlevel-warnings?date=${this.rangeDate[0]}`;
    console.log(url);
      fetch(url)
        .then((response) => response.json())
        .then((response)=> {
          this.geoglowsFloodWarnings = [
            this.utilsApp.filterByDay(response, "d01"),
            this.utilsApp.filterByDay(response, "d02"),
            this.utilsApp.filterByDay(response, "d03"),
            this.utilsApp.filterByDay(response, "d04"),
            this.utilsApp.filterByDay(response, "d05"),
            this.utilsApp.filterByDay(response, "d06"),
            this.utilsApp.filterByDay(response, "d07"),
            this.utilsApp.filterByDay(response, "d08"),
            this.utilsApp.filterByDay(response, "d09"),
            this.utilsApp.filterByDay(response, "d10"),
            this.utilsApp.filterByDay(response, "d11"),
            this.utilsApp.filterByDay(response, "d12"),
            this.utilsApp.filterByDay(response, "d13"),
            this.utilsApp.filterByDay(response, "d14"),
            this.utilsApp.filterByDay(response, "d15")
          ];
          this.updateFloodWarnings();
        })
  }

  public floodIcon(data:any, rp:string){
    const layers = this.utilsApp.filterByRP(data, rp);
    const LgeoJSON = L.geoJSON(layers, {
      pointToLayer: (feature, latlng) => {
        return L.marker(latlng, {
          icon: L.icon({
            iconUrl: `assets/icons/station/${rp}.png`,
            iconSize: [12, 16],
            iconAnchor: [8, 8]})
        });
      }
    })
    return LgeoJSON;
  }


  public updateFloodWarnings(){
    const currentData = this.geoglowsFloodWarnings[this.activeDateIndex];
    this.geoglowsFlood000 && this.map.removeLayer(this.geoglowsFlood000);
    this.isActiveFlood000 && (this.geoglowsFlood000 = this.floodIcon(currentData, "R0").addTo(this.map));
    this.geoglowsFlood000.bringToFront();
    this.geoglowsFlood002 && this.map.removeLayer(this.geoglowsFlood002);
    this.isActiveFlood002 && (this.geoglowsFlood002 = this.floodIcon(currentData, "R2").addTo(this.map));
    this.geoglowsFlood002.bringToFront();
    this.geoglowsFlood005 && this.map.removeLayer(this.geoglowsFlood005);
    this.isActiveFlood005 && (this.geoglowsFlood005 = this.floodIcon(currentData, "R5").addTo(this.map));
    this.geoglowsFlood005.bringToFront();
    this.geoglowsFlood010 && this.map.removeLayer(this.geoglowsFlood010);
    this.isActiveFlood010 && (this.geoglowsFlood010 = this.floodIcon(currentData, "R10").addTo(this.map));
    this.geoglowsFlood010.bringToFront();
    this.geoglowsFlood025 && this.map.removeLayer(this.geoglowsFlood025);
    this.isActiveFlood025 && (this.geoglowsFlood025 = this.floodIcon(currentData, "R25").addTo(this.map));
    this.geoglowsFlood025.bringToFront();
    this.geoglowsFlood050 && this.map.removeLayer(this.geoglowsFlood050);
    this.isActiveFlood050 && (this.geoglowsFlood050 = this.floodIcon(currentData, "R50").addTo(this.map));
    this.geoglowsFlood050.bringToFront();
    this.geoglowsFlood100 && this.map.removeLayer(this.geoglowsFlood100);
    this.isActiveFlood100 && (this.geoglowsFlood100 = this.floodIcon(currentData, "R100").addTo(this.map));
    this.geoglowsFlood100.bringToFront();

    this.legendControl.onAdd = () => {
      const infoDiv = document.createElement('div');
      infoDiv.style.backgroundColor = 'rgba(255, 255, 255, 0.9)';
      infoDiv.style.color = 'black';
      infoDiv.style.padding = '5px';
      infoDiv.style.borderRadius = "5px"
      infoDiv.innerHTML = `<b>Alertas por inundación</b><br>
                            <b>Inicialización:</b> ${this.rangeDate[0]}<br>
                            <b>Pronóstico:</b> ${this.rangeDate[this.activeDateIndex]}`;
      return(infoDiv)
    }
    this.legendControl.addTo(this.map);

    this.geoglowsFlood000.on("click", (e: L.LeafletMouseEvent) => this.getParamAlert(e))
    this.geoglowsFlood002.on("click", (e: L.LeafletMouseEvent) => this.getParamAlert(e))
    this.geoglowsFlood005.on("click", (e: L.LeafletMouseEvent) => this.getParamAlert(e))
    this.geoglowsFlood010.on("click", (e: L.LeafletMouseEvent) => this.getParamAlert(e))
    this.geoglowsFlood025.on("click", (e: L.LeafletMouseEvent) => this.getParamAlert(e))
    this.geoglowsFlood050.on("click", (e: L.LeafletMouseEvent) => this.getParamAlert(e))
    this.geoglowsFlood100.on("click", (e: L.LeafletMouseEvent) => this.getParamAlert(e))
  }

  public updateFloodWarningsDay(){
    if(this.dateControl.value){
      this.rangeDate = this.utilsApp.getDateRangeGeoglows(this.dateControl.value);
      this.activeDateIndex = 0;
      this.getFloodWarnings();
      this.dateControlPanel.setValue(this.dateControl.value);
    }
    console.log("Actualizado")
  }




  public nextTimeControl(){
    this.activeDateIndex++;
    if (this.activeDateIndex >= this.geoglowsFloodWarnings.length) {
      this.activeDateIndex = 0;
    }
    this.updateFloodWarnings();
  }

  public previuosTimeControl(){
    this.activeDateIndex--;
    if (this.activeDateIndex < 0) {
      this.activeDateIndex = this.geoglowsFloodWarnings.length - 1;
    }
    this.updateFloodWarnings();
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
          style: { color: '#000000', weight: 2.5, fillOpacity: 0.1},
        }).addTo(this.map);
        this.map.fitBounds(this.geojsonLayer.getBounds());
      });
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
          console.log("Funciona")

          let legendElement = document.createElement('div');
          let imgElement = document.createElement('div');

          this.ffgsLegend = new L.Control({ position: 'bottomright' });
          this.ffgsLegend.onAdd = () => legendElement;
          this.ffgsLegend.addTo(this.map);

          this.imgLegend = new L.Control({ position: 'bottomright' });
          this.imgLegend.onAdd = () => imgElement;
          this.imgLegend.addTo(this.map);

          legendElement.style.backgroundColor = 'rgba(255, 255, 255, 0.9)';
          legendElement.style.color = 'black';
          legendElement.style.padding = '5px';
          legendElement.style.borderRadius = "5px"

          imgElement.style.backgroundColor = 'rgba(255, 255, 255, 0.9)';
          imgElement.style.color = 'black';
          imgElement.style.padding = '5px';
          imgElement.style.borderRadius = "5px"

          const imageElement = document.createElement('img');
          imageElement.src = `assets/img/${param}.png`;
          imageElement.height = 250;
          imgElement.innerHTML = "";
          if(imgCond){
            imgElement.appendChild(imageElement);
          }


          if(type==="ffgs"){
            legendElement.innerHTML = `<b>${title}</b> <br> <b>Última actualización:</b> ${this.utilsApp.getFFGSDate()}`;
          }

          if(type==="pacum24"){
            legendElement.innerHTML = `<b>${title}</b>${this.utilsApp.getAcumulatedDate7()}`;
          }

          if(type==="pacum48"){
            legendElement.innerHTML = `<b>${title}</b>${this.utilsApp.getAcumulatedDate48()}`;
          }

          if(type==="pacum72"){
            legendElement.innerHTML = `<b>${title}</b>${this.utilsApp.getAcumulatedDate72()}`;
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
    }
  }


  public downloadHistoricalSimulation(){
    const url = `${environment.urlAPI}/geoglows/get-historical-simulation-csv?comid=${this.comid}`
    const link = document.createElement('a');
    link.href = url;
    link.click();
  }

  public downloadForecast(){
    if(this.dateControlPanel.value){
      const currentDate = this.utilsApp.getDateRangeGeoglows(this.dateControlPanel.value);
      const url = `${environment.urlAPI}/geoglows/get-forecast-csv?comid=${this.comid}&date=${currentDate[0]}`
      const link = document.createElement('a');
      link.href = url;
      link.click();
    }
  }



}
