// Required libraries and modules
import { Router } from '@angular/router';
import { Modal } from 'bootstrap';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../services/auth.service';
import { JwtHelperService } from '@auth0/angular-jwt';
import { Component, ElementRef, EventEmitter, Input, Output, ViewChild } from '@angular/core';


@Component({
  selector: 'app-app-template',
  standalone: true,
  imports: [CommonModule],
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
  public isOpen: boolean = false;
  public isPanelActive: boolean = true;
  @Output() panelActivate = new EventEmitter<boolean>();

  // State variables
  public isAuth: boolean = false;
  public userFullName: string = "";
  public username: string = "";
  public staff: boolean = false;

  // Modals panels
  @ViewChild('dataModal') dataModal?: ElementRef;
  @ViewChild('infoModal') infoModal?: ElementRef;
  @ViewChild('videoProgressModal') videoProgressModal?: ElementRef;


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
  public toggleDropdown(): void {
    this.isPanelActive = !this.isPanelActive;
    this.panelActivate.emit(this.isPanelActive);
  }

  // Logout function
  public logout(): void {
    this.authService.logout();
  }

  // Close app and redirect to app panel
  public redirectToApps(): void {
    this.router.navigateByUrl('/apps');
  }

  // Show data modal
  public showDataModal(): void {
    if (this.dataModal) {
      const modal = new Modal(this.dataModal.nativeElement);
      modal.show();
    }
  }

  // Show info modal
  public showInfoModal(): void {
    if (this.infoModal) {
      const modal = new Modal(this.infoModal.nativeElement);
      modal.show();
    }
  }

  public showVideoProgressModal(): void {
    if (this.videoProgressModal) {
      const modal = new Modal(this.videoProgressModal.nativeElement);
      modal.show();
    }
  }

  public hideVideoProgressModal(): void {
    if (this.videoProgressModal) {
      const modal = new Modal(this.videoProgressModal.nativeElement);
      modal.hide();
    }
  }

  // Login and redirect
  public loginRedirect(){
    this.router.navigateByUrl(`/login?next=${this.appUrl}`);
  }
}
