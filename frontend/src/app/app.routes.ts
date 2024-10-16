import { Routes } from '@angular/router';
import { HomeComponent } from './views/home/home.component';
import { LoginComponent } from './views/login/login.component';
import { RegisterComponent } from './views/register/register.component';
import { AppsComponent } from './views/apps/apps.component';
import { ClimateTrendsComponent } from './apps/climate-trends/climate-trends.component';
import { MetDataExplorerComponent } from './apps/met-data-explorer/met-data-explorer.component';
import { HydroviewerComponent } from './apps/hydroviewer/hydroviewer.component';
import { HistoricalValidationToolComponent } from './apps/historical-validation-tool/historical-validation-tool.component';
import { NationalWaterLevelForecastComponent } from './apps/national-water-level-forecast/national-water-level-forecast.component';
import { HydropowerDataExplorerComponent } from './apps/hydropower-data-explorer/hydropower-data-explorer.component';
import { HydrometReportToolComponent } from './apps/hydromet-report-tool/hydromet-report-tool.component';

export const routes: Routes = [
  { path: "", component: HomeComponent },
  { path: "login", component: LoginComponent },
  { path: "register", component: RegisterComponent },
  { path: "apps", component: AppsComponent },

  { path: "apps/climate-trends", component: ClimateTrendsComponent },
  { path: "apps/met-data-explorer", component: MetDataExplorerComponent },
  { path: "apps/hydroviewer", component: HydroviewerComponent },
  { path: "apps/historical-validation-tool", component: HistoricalValidationToolComponent },
  { path: "apps/national-water-level-forecast", component: NationalWaterLevelForecastComponent},
  { path: "apps/hydropower-data-explorer", component: HydropowerDataExplorerComponent},
  { path: "apps/hydromet-report-tool", component: HydrometReportToolComponent},

  { path: "**", redirectTo: "", pathMatch: "full" }
];
