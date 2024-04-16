import { Routes } from '@angular/router';
import { DashboardComponent } from './dashboard.component';
import { authGuard } from '../../auth/guard/auth.guard';
import { ClimateTrendsComponent } from '../climate-trends/climate-trends.component';
import { MetDataExplorerComponent } from '../met-data-explorer/met-data-explorer.component';


export const DASHBOARD_ROUTES: Routes = [
  {path:"", component: DashboardComponent, canActivate:[authGuard]},
  {path:"climate-trends", component: ClimateTrendsComponent, canActivate:[authGuard]},
  {path:"met-data-explorer", component: MetDataExplorerComponent, canActivate:[authGuard]}
]
