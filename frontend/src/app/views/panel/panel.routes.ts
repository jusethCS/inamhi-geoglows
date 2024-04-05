import { Routes } from '@angular/router';
import { PanelComponent } from './panel.component';
import { authGuard } from '../../auth/guard/auth.guard';


export const PANEL_ROUTES: Routes = [
  {path:"", component: PanelComponent, canActivate:[authGuard]}
]
