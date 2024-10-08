import { Component } from '@angular/core';
import { HeaderComponent } from '../../shared/header/header.component';
import { CardappComponent } from '../../shared/cardapp/cardapp.component';

@Component({
  selector: 'app-apps',
  standalone: true,
  imports: [HeaderComponent, CardappComponent],
  templateUrl: './apps.component.html',
  styleUrl: './apps.component.css'
})
export class AppsComponent {

}
