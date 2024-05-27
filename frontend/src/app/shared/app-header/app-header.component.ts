import { Component, EventEmitter, Input, Output } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../auth/auth.service';
import { JwtHelperService } from '@auth0/angular-jwt';

import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { faChartColumn } from '@fortawesome/free-solid-svg-icons';
import { faBars } from '@fortawesome/free-solid-svg-icons';
import { faXmark } from '@fortawesome/free-solid-svg-icons';
import { faUser } from '@fortawesome/free-solid-svg-icons';


@Component({
  selector: 'app-header',
  standalone: true,
  imports: [FontAwesomeModule],
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
  @Output() showPanel = new EventEmitter<string>();

  // Boolean variables for dropdown and panel components
  isOpen: boolean = false;
  isPanelActive: boolean = true;

  // State variables
  isAuth:boolean = false;
  userFullName:string = "";
  username:string = "";
  staff:boolean = false;

  // Icons
  faChartColumn = faChartColumn;
  faBars = faBars;
  faXmark = faXmark;
  faUser = faUser;




  // -------------------------------------------------------------------- //
  //                            CONSTRUCTOR                               //
  // -------------------------------------------------------------------- //

  // Services injections
  constructor(
    private router: Router,
    private authService: AuthService,
    private jwtHelper:JwtHelperService) {
      this.isAuth = this.authService.isAuth();
    }


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

  showModalPanel(){
    this.showPanel.emit("click");
  }

}
