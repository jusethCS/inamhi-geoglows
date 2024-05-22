import { Routes } from '@angular/router';
import { HomeComponent } from './views/home/home.component';
import { LoginComponent } from './auth/login/login.component';
import { RegisterComponent } from './auth/register/register.component';

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
  }
];
