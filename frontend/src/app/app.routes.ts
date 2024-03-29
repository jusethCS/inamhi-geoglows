import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path:'',
    loadChildren: () => import("./views/home/home.routes").then(m => m.HOME_ROUTES)
  }
];
