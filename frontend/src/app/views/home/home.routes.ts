import { Routes } from '@angular/router';
import { HomeComponent } from './home.component';
import { AuthComponent } from '../../auth/components/auth/auth.component';
import { RegisterComponent } from '../../auth/components/register/register.component';

export const HOME_ROUTES: Routes = [
  {path:"", component: HomeComponent, children:[
    {path: "", component: AuthComponent},
    {path: "register", component: RegisterComponent}
  ]}
]
