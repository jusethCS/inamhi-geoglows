import { Component, EventEmitter, Input, Output } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../../auth/services/auth.service';
import { JwtHelperService } from '@auth0/angular-jwt';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [],
  templateUrl: './app-header.component.html',
  styleUrl: './app-header.component.css'
})

export class AppHeaderComponent {

  // -------------------------------------------------------------------- //
  //                           CLASS ATTRIBUTES                           //
  // -------------------------------------------------------------------- //

  // Variables for comunication
  @Input() appName: string | undefined;
  @Input() imageUrl: string | undefined;
  @Output() panelActivate = new EventEmitter<boolean>();

  // Boolean variables for dropdown and panel components
  isOpen: boolean = false;
  isPanelActive: boolean = true;

  // State variables
  userFullName = "";
  username = "";
  staff = false;



  // -------------------------------------------------------------------- //
  //                            CONSTRUCTOR                               //
  // -------------------------------------------------------------------- //

  // Services injections
  constructor(
    private router: Router,
    private authService: AuthService,
    private jwtHelper:JwtHelperService) {}


  // Initialice the component
  ngOnInit() {
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
    // Set the panel status
    this.panelActivate.emit(this.isPanelActive);
  }



  // -------------------------------------------------------------------- //
  //                               METHODS                                //
  // -------------------------------------------------------------------- //

  // Open or close user profile options
  toggleDropdown() {
    this.isOpen = !this.isOpen;
  }

  // Open or close control panel (for map)
  togglePanel(){
    this.isPanelActive = !this.isPanelActive;
    this.panelActivate.emit(this.isPanelActive);
  }

  // Logout function
  logout(){
    this.authService.logout();
  }

  // Close app and redirect to app panel
  redirectToApps(){
    this.router.navigateByUrl('/apps');
  }

}
