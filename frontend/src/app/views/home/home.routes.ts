import { Routes } from '@angular/router';
import { HomeComponent } from './home.component';
import { LoginComponent } from '../../auth/components/login/login.component';
import { RegisterComponent } from '../../auth/components/register/register.component';
import { homeGuard } from '../../auth/guard/home.guard';

export const HOME_ROUTES: Routes = [
  {path:"", component: HomeComponent,
    canActivate:[homeGuard],
    children:[
      {path: "", component: LoginComponent},
      {path: "register", component: RegisterComponent}
    ]}
]
