import { Routes } from '@angular/router';

export const routes: Routes = [
  { path:'', loadChildren: () => import("./views/home/home.routes").then(m => m.HOME_ROUTES) },
  { path:'apps', loadChildren: () => import("./views/panel/panel.routes").then(m => m.PANEL_ROUTES)}
];
