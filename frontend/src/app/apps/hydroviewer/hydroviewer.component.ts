import { Component } from '@angular/core';
import { AppTemplateComponent } from "../../components/template/app-template.component";

@Component({
  selector: 'app-hydroviewer',
  standalone: true,
  imports: [AppTemplateComponent],
  templateUrl: './hydroviewer.component.html',
  styleUrl: './hydroviewer.component.css'
})
export class HydroviewerComponent {

}
