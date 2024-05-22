import { Component, EventEmitter, HostListener, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { faUser } from '@fortawesome/free-solid-svg-icons';
import { Router } from '@angular/router';
import { AuthService } from '../../auth/auth.service';
import { JwtHelperService } from '@auth0/angular-jwt';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [CommonModule, FontAwesomeModule],
  templateUrl: './header.component.html',
  styleUrl: './header.component.css'
})

export class HeaderComponent {

  // -------------------------------------------------------------------- //
  //                           CLASS ATTRIBUTES                           //
  // -------------------------------------------------------------------- //

  // State variables
  isAuth:boolean = false;
  userFullName:string = ""
  username:string = "";
  staff = false;
  scrolled:boolean = false;

  // icons
  userIcon = faUser;

  // Emitter
  @Output() outIsAuth = new EventEmitter<boolean>();
  @Output() clickLogin = new EventEmitter<string>();


  // -------------------------------------------------------------------- //
  //                            CONSTRUCTOR                               //
  // -------------------------------------------------------------------- //

  // Services injections
  constructor(
    private router: Router,
    private authService: AuthService,
    private jwtHelper:JwtHelperService) {
    }

  // Initialice the component
  ngOnInit() {
    // Determinate if user is auth
    this.isAuth = this.authService.isAuth();
    this.outIsAuth.emit(this.isAuth);

    // Get and use the user profile
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

  @HostListener('window:scroll', [])
  onWindowScroll() {
    this.scrolled = window.scrollY > 50;
  }


  // -------------------------------------------------------------------- //
  //                               METHODS                                //
  // -------------------------------------------------------------------- //
  logout(){
    this.authService.logout();
    window.location.reload();
  }

  clickOnLoginButton(){
    this.clickLogin.emit("click")
  }

}
