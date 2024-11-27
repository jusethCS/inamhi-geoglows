import { Component, ElementRef, ViewChild } from '@angular/core';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { AuthService } from '../../auth/auth.service';
import { AppTemplateComponent } from "../../shared/app-template/app-template.component";
import { DropdownComponent } from "../../shared/dropdown/dropdown.component";


@Component({
  selector: 'app-hydromet-report-tool',
  standalone: true,
  imports: [
    AppTemplateComponent,
    DropdownComponent,
    CommonModule,
    FormsModule
  ],
  templateUrl: './hydromet-report-tool.component.html',
  styleUrl: './hydromet-report-tool.component.css'
})
export class HydrometReportToolComponent {
  public isAuth: boolean;
  public appUrl:string = '/apps/hydromet-warning-tool';

  public isActiveHydropowerDaily: boolean = true;
  public isActiveHydropowerWeekly: boolean = false;

  public datesDaily:string[] = [];
  public forecastDaily:string[] = [];

  // Daily
  @ViewChild('mazarDaily', { static: false}) mazarDaily!: ElementRef;
  @ViewChild("pauteDaily", {static: false}) pauteDaily!: ElementRef;
  @ViewChild("sopladoraDaily", {static: false}) sopladoraDaily!: ElementRef;
  @ViewChild("cocacodoDaily", {static: false}) cocacodoDaily!: ElementRef;
  @ViewChild("pucaraDaily", {static: false}) pucaraDaily!: ElementRef;
  @ViewChild("agoyanDaily", {static: false}) agoyanDaily!: ElementRef;
  @ViewChild("minasDaily", {static: false}) minasDaily!: ElementRef;
  @ViewChild("delsitanisaguaDaily", {static: false}) delsitanisaguaDaily!: ElementRef;
  @ViewChild("toachiDaily", {static: false}) toachiDaily!: ElementRef;

  // -------------------------------------------------------------------- //
  //                            CONSTRUCTOR                               //
  // -------------------------------------------------------------------- //
  constructor(
    private authService: AuthService,
    private router: Router,
  ){
    this.isAuth = this.authService.isAuth();
    console.log(this.isAuth);
    if (!this.isAuth) {
      this.router.navigateByUrl(`/login?next=${this.appUrl}`);
    }
    this.datesDaily = this.formatDates(new Date());

    fetch("/assets/reports/forecast-daily.csv?timestamp=${new Date().getTime()}")
      .then(response => response.text())  // Obtener el texto del CSV
      .then(csvData => {
        const rows = csvData.split('\n');
        const result: string[] = [];
        for (let i = 1; i < rows.length; i++) {
          const columns = rows[i].split(',');
          if (columns.length === 2) {
            result.push(columns[1]);
          }
        }
        this.forecastDaily = result;
      })
      .catch(error => {
        console.error('Error al obtener el archivo CSV:', error);
      });
  }



  public updateReport(param:string){
    param !== "hydropowers-daily" && (this.isActiveHydropowerDaily = false);
    param !== "hydropowers-weekly" && (this.isActiveHydropowerWeekly = false);
  }

  public formatDates(date: Date): string[] {
    const months = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"];
    const day = date.getDate();
    const month = months[date.getMonth()];
    const year = date.getFullYear();
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    const format1 = `${day} de ${month} del ${year}, ${hours}:${minutes}`;
    date.setDate(date.getDate() + 1);
    const startDay = date.getDate();
    const startMonth = months[date.getMonth()];
    const startYear = date.getFullYear();
    const endDate = new Date(date);
    endDate.setDate(date.getDate() + 1);
    const endDay = endDate.getDate();
    const endMonth = months[endDate.getMonth()];
    const endYear = endDate.getFullYear();
    const format2 = `desde las 07:00 del ${startDay} de ${startMonth} hasta las 07:00 del ${endDay} de ${endMonth} del ${endYear}`;
    const format3 = `desde el ${startDay} de ${startMonth} del ${startYear} (07H00) hasta el ${endDay} de ${endMonth} del ${endYear} (07H00)`;
    return [format1, format2, format3];
  }

  public buildUrl(baseUrl: string, params: any): string {
    const queryString = Object.keys(params)
      .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`)
      .join('&');
    return `${baseUrl}?${queryString}`;
  }


  public generateHydropowerDailyReport(){
    const params = {
      mazar : this.mazarDaily.nativeElement.innerText,
      paute: this.pauteDaily.nativeElement.innerText,
      sopladora: this.sopladoraDaily.nativeElement.innerText,
      cocacodo: this.cocacodoDaily.nativeElement.innerText,
      pucara: this.pucaraDaily.nativeElement.innerText,
      agoyan: this.agoyanDaily.nativeElement.innerText,
      minas: this.minasDaily.nativeElement.innerText,
      delsitanisagua: this.delsitanisaguaDaily.nativeElement.innerText,
      toachi: this.toachiDaily.nativeElement.innerText
    }
    const link = "https://inamhi.geoglows.org/api/geoglows/retrieve-daily-hydropower-report"
    const url = this.buildUrl(link, params)
    window.location.href = url
  }


}
