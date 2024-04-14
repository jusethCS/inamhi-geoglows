import { AuthService } from './../../auth/services/auth.service';
import { Component } from '@angular/core';
import { HeaderComponent } from '../../shared/components/header/header.component';
import { JwtHelperService } from '@auth0/angular-jwt';
import { CardappComponent } from '../../shared/components/cardapp/cardapp.component';


@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [HeaderComponent, CardappComponent],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css'
})


export class DashboardComponent {

  userFullName = "";
  username = "";
  staff = false;

  constructor(private authService: AuthService, private jwtHelper:JwtHelperService) {}

  ngOnInit() {
    const jwtToken = this.authService.getToken();
    if (jwtToken) {
      const decodedToken = this.jwtHelper.decodeToken(jwtToken)
      if(decodedToken){
        this.userFullName = decodedToken.firstname + " " + decodedToken.lastname
        this.username = decodedToken.username
        this.staff = decodedToken.staff
      }
    }
  }

}
