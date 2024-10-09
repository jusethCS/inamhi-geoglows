// Required libraries and modules
import { Router } from '@angular/router';
import { Modal } from 'bootstrap';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../auth/auth.service';
import { JwtHelperService } from '@auth0/angular-jwt';
import { Component, ElementRef, EventEmitter, Input, Output, ViewChild } from '@angular/core';

// Font Awesome Icons
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { faChartColumn, faBars, faXmark, faUser } from '@fortawesome/free-solid-svg-icons';
import { faCircleQuestion } from '@fortawesome/free-regular-svg-icons';


@Component({
  selector: 'app-app-template',
  standalone: true,
  imports: [
    CommonModule,
    FontAwesomeModule
  ],
  templateUrl: './app-template.component.html',
  styleUrls: ['./app-template.component.css']
})


export class AppTemplateComponent {

  // -------------------------------------------------------------------- //
  //                           CLASS ATTRIBUTES                           //
  // -------------------------------------------------------------------- //

  // Variables for communication
  @Input() appName?: string;
  @Input() imageUrl?: string;
  @Input() appUrl?: string;

  // Boolean variables for dropdown and panel components
  isOpen: boolean = false;
  isPanelActive: boolean = true;
  @Output() panelActivate = new EventEmitter<boolean>();

  // State variables
  isAuth: boolean = false;
  userFullName: string = "";
  username: string = "";
  staff: boolean = false;

  // Modals panels
  @ViewChild('dataModal') dataModal?: ElementRef;
  @ViewChild('infoModal') infoModal?: ElementRef;
  @ViewChild('videoProgressModal') videoProgressModal?: ElementRef;


  // Icons
  faChartColumn = faChartColumn;
  faBars = faBars;
  faXmark = faXmark;
  faUser = faUser;
  faCircleQuestion = faCircleQuestion;

  // -------------------------------------------------------------------- //
  //                            CONSTRUCTOR                               //
  // -------------------------------------------------------------------- //

  // Service injections
  constructor(
    private router: Router,
    private authService: AuthService,
    private jwtHelper: JwtHelperService
  ) {
    this.isAuth = this.authService.isAuth();
  }

  // Initialize the component
  ngOnInit(): void {
    // Get and use the user profile
    const jwtToken = this.authService.getToken();
    if (jwtToken) {
      const decodedToken = this.jwtHelper.decodeToken(jwtToken);
      if (decodedToken) {
        this.userFullName = `${decodedToken.firstname} ${decodedToken.lastname}`;
        this.username = decodedToken.username;
        this.staff = decodedToken.staff;
      }
    }
  }

  // -------------------------------------------------------------------- //
  //                               METHODS                                //
  // -------------------------------------------------------------------- //

  // Toggle panel visibility
  toggleDropdown(): void {
    this.isPanelActive = !this.isPanelActive;
    this.panelActivate.emit(this.isPanelActive);
  }

  // Logout function
  logout(): void {
    this.authService.logout();
  }

  // Close app and redirect to app panel
  redirectToApps(): void {
    this.router.navigateByUrl('/apps');
  }

  // Show data modal
  showDataModal(): void {
    if (this.dataModal) {
      const modal = new Modal(this.dataModal.nativeElement);
      modal.show();
    }
  }

  // Show info modal
  showInfoModal(): void {
    if (this.infoModal) {
      const modal = new Modal(this.infoModal.nativeElement);
      modal.show();
    }
  }

  showVideoProgressModal(): void {
    if (this.videoProgressModal) {
      const modal = new Modal(this.videoProgressModal.nativeElement);
      modal.show();
    }
  }

  hideVideoProgressModal(): void {
    if (this.videoProgressModal) {
      const modal = new Modal(this.videoProgressModal.nativeElement);
      modal.hide();
    }
  }

  // Login and redirect
  loginRedirect(){
    this.router.navigateByUrl(`/login?next=${this.appUrl}`);
  }
}
