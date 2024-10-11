import { Routes } from '@angular/router';
import { HomeComponent } from './views/home/home.component';
import { LoginComponent } from './auth/login/login.component';
import { RegisterComponent } from './auth/register/register.component';
import { AppsComponent } from './views/apps/apps.component';
import { ClimateTrendsComponent } from './views/climate-trends/climate-trends.component';
import { MetDataExplorerComponent } from './views/met-data-explorer/met-data-explorer.component';
import { LoginRedirectComponent } from './views/login-redirect/login-redirect.component';
import { HydroviewerComponent } from './views/hydroviewer/hydroviewer.component';
import { HistoricalValidationToolComponent } from './views/historical-validation-tool/historical-validation-tool.component';
import { NationalWaterLevelForecastComponent } from './views/national-water-level-forecast/national-water-level-forecast.component';
import { HydrometReportToolComponent } from './views/hydromet-report-tool/hydromet-report-tool.component';
import { HydropowersComponent } from './views/hydropowers/hydropowers.component';

export const routes: Routes = [
  // ----------------------------------------------------------------------- //
  //                                  HOME                                   //
  // ----------------------------------------------------------------------- //
  {
    path: "",
    component: HomeComponent,
    children:[
      {path: "", component: LoginComponent},
      {path: "register", component: RegisterComponent}
    ]
  },
  {
    path: "login",
    component: LoginRedirectComponent
  },
  // ----------------------------------------------------------------------- //
  //                             APPS DASHBOARD                              //
  // ----------------------------------------------------------------------- //
  {
    path: "apps",
    component: AppsComponent,
  },
  // ----------------------------------------------------------------------- //
  //                                  APPS                                   //
  // ----------------------------------------------------------------------- //
  {
    path: "apps/climate-trends",
    component: ClimateTrendsComponent,
  },
  {
    path: "apps/met-data-explorer",
    component: MetDataExplorerComponent,
  },
  {
    path: "apps/hydroviewer",
    component: HydroviewerComponent,
  },
  {
    path: "apps/historical-validation-tool",
    component: HistoricalValidationToolComponent,
  },
  {
    path: "apps/national-water-level-forecast",
    component: NationalWaterLevelForecastComponent,
  },
  {
    path: "apps/hydromet-warning-tool",
    component: HydrometReportToolComponent,
  },
  {
    path: "apps/hydropowers",
    component: HydropowersComponent,
  },
];
