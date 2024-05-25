import { Routes } from '@angular/router';
import { HomeComponent } from './views/home/home.component';
import { LoginComponent } from './auth/login/login.component';
import { RegisterComponent } from './auth/register/register.component';
import { AppsComponent } from './views/apps/apps.component';
import { ClimateTrendsComponent } from './views/climate-trends/climate-trends.component';

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
];
