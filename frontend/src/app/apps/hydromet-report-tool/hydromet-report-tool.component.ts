import { Component, ElementRef, ViewChild } from '@angular/core';
import { AppTemplateComponent } from "../../components/template/app-template.component";
import { DropdownComponent } from "../../components/dropdown/dropdown.component";
import { AuthService } from '../../services/auth.service';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ImageComponent } from "../../components/image/image.component";
import { formatDates, buildUrl, formatDatesWeekly } from './hydromet-report-tool.utils';


@Component({
  selector: 'app-hydromet-report-tool',
  standalone: true,
  imports: [
    AppTemplateComponent,
    DropdownComponent,
    CommonModule,
    FormsModule,
    ImageComponent
  ],
  templateUrl: './hydromet-report-tool.component.html',
  styleUrl: './hydromet-report-tool.component.css'
})


export class HydrometReportToolComponent {
  // Control variables
  public isAuth: boolean;
  public appUrl:string = '/apps/hydromet-report-tool';

  // State variables for panel activation
  public isActiveHydropowerDaily: boolean = true;
  public isActiveHydropowerWeekly: boolean = false;

  // Hydropower daily forecast
  public datesHydropowerDailyForecast:string[] = [];
  public hydropowerDailyForecast:string[] = [];
  @ViewChild('mazarDaily', { static: false}) mazarDaily!: ElementRef;
  @ViewChild("pauteDaily", {static: false}) pauteDaily!: ElementRef;
  @ViewChild("sopladoraDaily", {static: false}) sopladoraDaily!: ElementRef;
  @ViewChild("cocacodoDaily", {static: false}) cocacodoDaily!: ElementRef;
  @ViewChild("pucaraDaily", {static: false}) pucaraDaily!: ElementRef;
  @ViewChild("agoyanDaily", {static: false}) agoyanDaily!: ElementRef;
  @ViewChild("minasDaily", {static: false}) minasDaily!: ElementRef;
  @ViewChild("delsitanisaguaDaily", {static: false}) delsitanisaguaDaily!: ElementRef;

  // Hydropower weekly forecast
  public datesHydropowerWeeklyForecast:string[] = [];
  public hydropowerWeeklyForecast:string[] = [];
  @ViewChild('mazarWeekly', { static: false}) mazarWeekly!: ElementRef;
  @ViewChild("pauteWeekly", {static: false}) pauteWeekly!: ElementRef;
  @ViewChild("sopladoraWeekly", {static: false}) sopladoraWeekly!: ElementRef;
  @ViewChild("cocacodoWeekly", {static: false}) cocacodoWeekly!: ElementRef;
  @ViewChild("pucaraWeekly", {static: false}) pucaraWeekly!: ElementRef;
  @ViewChild("agoyanWeekly", {static: false}) agoyanWeekly!: ElementRef;
  @ViewChild("minasWeekly", {static: false}) minasWeekly!: ElementRef;
  @ViewChild("delsitanisaguaWeekly", {static: false}) delsitanisaguaWeekly!: ElementRef;


  constructor(private authService: AuthService, private router: Router){
    this.isAuth = this.authService.isAuth();
    if (!this.isAuth) {
      this.router.navigateByUrl(`/login?next=${this.appUrl}`);
    }

    // HYDROPOWER DAILY FORECAST
    this.datesHydropowerDailyForecast = formatDates(new Date());
    fetch("https://inamhi.geoglows.org/api/hydromet-report-tool/hydropower-daily-forecast")
      .then(response => response.json())
      .then(response => {
        this.hydropowerDailyForecast = response.forecasts.map(
          (forecast: { forecast: any; }) => forecast.forecast
        )
      })

    // HYDROPOWER WEEKLY FORECAST
    this.datesHydropowerWeeklyForecast = formatDatesWeekly(new Date());
    fetch("https://inamhi.geoglows.org/api/hydromet-report-tool/hydropower-weekly-forecast")
      .then(response => response.json())
      .then(response => {
        this.hydropowerWeeklyForecast = response.forecasts.map(
          (forecast: { forecast: any; }) => forecast.forecast
        )
      })

  }

  public updateReport(param:string){
    param !== "hydropowers-daily" && (this.isActiveHydropowerDaily = false);
    param !== "hydropowers-weekly" && (this.isActiveHydropowerWeekly = false);
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
      delsitanisagua: this.delsitanisaguaDaily.nativeElement.innerText
    }
    const link = "https://inamhi.geoglows.org/api/hydromet-report-tool/hydropower-daily-forecast-report"
    const url = buildUrl(link, params)
    window.location.href = url
  }

  public generateHydropowerWeeklyReport(){
    const params = {
      mazar : this.mazarWeekly.nativeElement.innerText,
      paute: this.pauteWeekly.nativeElement.innerText,
      sopladora: this.sopladoraWeekly.nativeElement.innerText,
      cocacodo: this.cocacodoWeekly.nativeElement.innerText,
      pucara: this.pucaraWeekly.nativeElement.innerText,
      agoyan: this.agoyanWeekly.nativeElement.innerText,
      minas: this.minasWeekly.nativeElement.innerText,
      delsitanisagua: this.delsitanisaguaWeekly.nativeElement.innerText
    }
    const link = "https://inamhi.geoglows.org/api/hydromet-report-tool/hydropower-weekly-forecast-report"
    const url = buildUrl(link, params)
    window.location.href = url
  }


}
