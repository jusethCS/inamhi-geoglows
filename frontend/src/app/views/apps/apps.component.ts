import { Component } from '@angular/core';
import { HeaderComponent } from '../../components/header/header.component';
import { CardappComponent } from '../../components/cardapp/cardapp.component';

@Component({
  selector: 'app-apps',
  standalone: true,
  imports: [HeaderComponent, CardappComponent],
  templateUrl: './apps.component.html',
  styleUrl: './apps.component.css'
})
export class AppsComponent {

}
