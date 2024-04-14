import { Routes } from '@angular/router';
import { DashboardComponent } from './dashboard.component';
import { authGuard } from '../../auth/guard/auth.guard';


export const DASHBOARD_ROUTES: Routes = [
  {path:"", component: DashboardComponent, canActivate:[authGuard]}
]
