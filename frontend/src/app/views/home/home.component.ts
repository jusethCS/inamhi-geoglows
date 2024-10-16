import { Component, ElementRef, ViewChild } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { HeaderComponent } from "../../components/header/header.component";
import { SlideinComponent } from "../../components/slidein/slidein.component";

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [HeaderComponent, SlideinComponent, MatButtonModule],
  templateUrl: './home.component.html',
  styleUrl: './home.component.css'
})
export class HomeComponent {

  // State variables
  loginPanelActive: boolean = false;
  isAuth: boolean = false;

  constructor() {}

  // Methods
  @ViewChild('about') myScrollContainer!: ElementRef;
  public scrollToElement(): void {
    const element = this.myScrollContainer.nativeElement;
    element.scrollIntoView({ behavior: 'auto', block: 'start' });
  }

  public retrieveIsAuth(isAuthD: boolean) {
    this.isAuth = isAuthD;
  }

  public showLoginPanel(click: string) {
    if (!this.isAuth && !this.loginPanelActive) this.loginPanelActive = true;
  }

  public githubRedirect() {
    window.location.href = 'https://github.com/jusethCS/inamhi-geoglows';
  }

}
