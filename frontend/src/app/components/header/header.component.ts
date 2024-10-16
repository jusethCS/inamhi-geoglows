import { Component, EventEmitter, HostListener, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { JwtHelperService } from '@auth0/angular-jwt';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './header.component.html',
  styleUrl: './header.component.css'
})

export class HeaderComponent {

  // State variables
  public isAuth:boolean = false;
  public userFullName:string = ""
  public username:string = "";
  public staff = false;
  public scrolled:boolean = false;

  // Emitter
  @Output() outIsAuth = new EventEmitter<boolean>();
  @Output() clickLogin = new EventEmitter<string>();

  // Services injections
  constructor(
    private router: Router,
    private authService: AuthService,
    private jwtHelper:JwtHelperService) {}

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

  // Methods
  @HostListener('window:scroll', [])
  public onWindowScroll() {
    this.scrolled = window.scrollY > 50;
  }

  public logout(){
    this.authService.logout();
    window.location.reload();
  }

  public clickOnLoginButton(){
    this.clickLogin.emit("click")
  }

  public redirectLogin(){
    this.router.navigate(['/login']);
  }

}
